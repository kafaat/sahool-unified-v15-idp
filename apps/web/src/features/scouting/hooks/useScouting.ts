/**
 * Scouting Feature - React Hooks
 * خطافات ميزة الكشافة الحقلية
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { scoutingApi } from '../api/scouting-api';
import type {
  ScoutingSession,
  Observation,
  ObservationFormData,
  ScoutingHistoryFilter,
  ScoutingStatistics,
  SessionSummary,
} from '../types/scouting';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const scoutingKeys = {
  all: ['scouting'] as const,
  sessions: () => [...scoutingKeys.all, 'sessions'] as const,
  session: (id: string) => [...scoutingKeys.sessions(), id] as const,
  activeSession: (fieldId: string) => [...scoutingKeys.sessions(), 'active', fieldId] as const,
  sessionSummary: (id: string) => [...scoutingKeys.session(id), 'summary'] as const,
  observations: (sessionId: string) => [...scoutingKeys.all, 'observations', sessionId] as const,
  history: (filters?: ScoutingHistoryFilter) => [...scoutingKeys.all, 'history', filters] as const,
  statistics: (fieldId?: string) => [...scoutingKeys.all, 'statistics', fieldId] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Session Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to get a scouting session by ID
 * خطاف للحصول على جلسة كشافة بواسطة المعرف
 */
export function useScoutingSession(sessionId: string) {
  return useQuery({
    queryKey: scoutingKeys.session(sessionId),
    queryFn: () => scoutingApi.getSession(sessionId),
    enabled: !!sessionId,
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 2,
  });
}

/**
 * Hook to get active scouting session for a field
 * خطاف للحصول على جلسة الكشافة النشطة لحقل
 */
export function useActiveSession(fieldId: string) {
  return useQuery({
    queryKey: scoutingKeys.activeSession(fieldId),
    queryFn: () => scoutingApi.getActiveSession(fieldId),
    enabled: !!fieldId,
    staleTime: 30 * 1000, // 30 seconds
    retry: 1,
  });
}

/**
 * Hook to get session summary
 * خطاف للحصول على ملخص الجلسة
 */
export function useSessionSummary(sessionId: string) {
  return useQuery({
    queryKey: scoutingKeys.sessionSummary(sessionId),
    queryFn: () => scoutingApi.getSessionSummary(sessionId),
    enabled: !!sessionId,
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 2,
  });
}

/**
 * Hook to start a scouting session
 * خطاف لبدء جلسة كشافة
 */
export function useStartSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, notes }: { fieldId: string; notes?: string }) =>
      scoutingApi.startSession(fieldId, notes),
    onSuccess: (data) => {
      // Invalidate active session query
      queryClient.invalidateQueries({ queryKey: scoutingKeys.activeSession(data.fieldId) });
      // Cache the new session
      queryClient.setQueryData(scoutingKeys.session(data.id), data);
    },
  });
}

/**
 * Hook to end a scouting session
 * خطاف لإنهاء جلسة كشافة
 */
export function useEndSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ sessionId, notes }: { sessionId: string; notes?: string }) =>
      scoutingApi.endSession(sessionId, notes),
    onSuccess: (data) => {
      // Update session cache
      queryClient.setQueryData(scoutingKeys.session(data.id), data);
      // Invalidate active session query
      queryClient.invalidateQueries({ queryKey: scoutingKeys.activeSession(data.fieldId) });
      // Invalidate history
      queryClient.invalidateQueries({ queryKey: scoutingKeys.history() });
    },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Observation Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to get observations for a session
 * خطاف للحصول على ملاحظات جلسة
 */
export function useObservations(sessionId: string) {
  return useQuery({
    queryKey: scoutingKeys.observations(sessionId),
    queryFn: () => scoutingApi.getObservations(sessionId),
    enabled: !!sessionId,
    staleTime: 30 * 1000, // 30 seconds
    retry: 2,
  });
}

/**
 * Hook to save a new observation
 * خطاف لحفظ ملاحظة جديدة
 */
export function useSaveObservation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ sessionId, data }: { sessionId: string; data: ObservationFormData }) =>
      scoutingApi.addObservation(sessionId, data),
    onMutate: async ({ sessionId }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: scoutingKeys.observations(sessionId) });

      // Snapshot the previous value
      const previousObservations = queryClient.getQueryData<Observation[]>(
        scoutingKeys.observations(sessionId)
      );

      return { previousObservations, sessionId };
    },
    onSuccess: (newObservation, { sessionId }) => {
      // Update observations cache
      queryClient.setQueryData<Observation[]>(
        scoutingKeys.observations(sessionId),
        (old) => [...(old || []), newObservation]
      );

      // Invalidate session to update counts
      queryClient.invalidateQueries({ queryKey: scoutingKeys.session(sessionId) });
      queryClient.invalidateQueries({ queryKey: scoutingKeys.sessionSummary(sessionId) });
    },
    onError: (_error, { sessionId }, context) => {
      // Rollback to previous value on error
      if (context?.previousObservations) {
        queryClient.setQueryData(
          scoutingKeys.observations(sessionId),
          context.previousObservations
        );
      }
    },
  });
}

/**
 * Hook to update an observation
 * خطاف لتحديث ملاحظة
 */
export function useUpdateObservation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      observationId,
      sessionId,
      data,
    }: {
      observationId: string;
      sessionId: string;
      data: Partial<ObservationFormData>;
    }) => scoutingApi.updateObservation(observationId, data),
    onSuccess: (updatedObservation, { sessionId }) => {
      // Update observations cache
      queryClient.setQueryData<Observation[]>(
        scoutingKeys.observations(sessionId),
        (old) =>
          old?.map((obs) => (obs.id === updatedObservation.id ? updatedObservation : obs)) || []
      );

      // Invalidate session summary
      queryClient.invalidateQueries({ queryKey: scoutingKeys.sessionSummary(sessionId) });
    },
  });
}

/**
 * Hook to delete an observation
 * خطاف لحذف ملاحظة
 */
export function useDeleteObservation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ observationId, sessionId }: { observationId: string; sessionId: string }) =>
      scoutingApi.deleteObservation(observationId),
    onSuccess: (_data, { observationId, sessionId }) => {
      // Update observations cache
      queryClient.setQueryData<Observation[]>(
        scoutingKeys.observations(sessionId),
        (old) => old?.filter((obs) => obs.id !== observationId) || []
      );

      // Invalidate session to update counts
      queryClient.invalidateQueries({ queryKey: scoutingKeys.session(sessionId) });
      queryClient.invalidateQueries({ queryKey: scoutingKeys.sessionSummary(sessionId) });
    },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// History & Statistics Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to get scouting history
 * خطاف للحصول على سجل الكشافة
 */
export function useScoutingHistory(filters?: ScoutingHistoryFilter) {
  return useQuery({
    queryKey: scoutingKeys.history(filters),
    queryFn: () => scoutingApi.getHistory(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });
}

/**
 * Hook to get scouting statistics
 * خطاف للحصول على إحصائيات الكشافة
 */
export function useScoutingStatistics(fieldId?: string) {
  return useQuery({
    queryKey: scoutingKeys.statistics(fieldId),
    queryFn: () => scoutingApi.getStatistics(fieldId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Report Generation Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to generate a scouting report
 * خطاف لإنشاء تقرير كشافة
 */
export function useGenerateReport() {
  return useMutation({
    mutationFn: ({
      sessionId,
      config,
    }: {
      sessionId: string;
      config?: {
        includePhotos?: boolean;
        includeMap?: boolean;
        language?: 'en' | 'ar' | 'both';
        format?: 'pdf' | 'excel';
      };
    }) => scoutingApi.generateReport(sessionId, config),
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Offline Sync Hook
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to sync offline data
 * خطاف لمزامنة البيانات غير المتصلة
 */
export function useSyncOfflineData() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => scoutingApi.syncOfflineData(),
    onSuccess: () => {
      // Invalidate all scouting queries to refetch fresh data
      queryClient.invalidateQueries({ queryKey: scoutingKeys.all });
    },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Composite Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Composite hook for managing a complete scouting session
 * خطاف مركب لإدارة جلسة كشافة كاملة
 */
export function useScoutingSessionManager(fieldId: string) {
  const { data: activeSession, isLoading: loadingActive } = useActiveSession(fieldId);
  const { data: observations, isLoading: loadingObservations } = useObservations(
    activeSession?.id || ''
  );
  const { data: summary } = useSessionSummary(activeSession?.id || '');

  const startSession = useStartSession();
  const endSession = useEndSession();
  const saveObservation = useSaveObservation();
  const updateObservation = useUpdateObservation();
  const deleteObservation = useDeleteObservation();

  return {
    // Session data
    session: activeSession,
    observations: observations || [],
    summary,
    isLoading: loadingActive || loadingObservations,

    // Session actions
    startSession: (notes?: string) => startSession.mutateAsync({ fieldId, notes }),
    endSession: (notes?: string) =>
      activeSession ? endSession.mutateAsync({ sessionId: activeSession.id, notes }) : Promise.reject(),

    // Observation actions
    addObservation: (data: ObservationFormData) =>
      activeSession
        ? saveObservation.mutateAsync({ sessionId: activeSession.id, data })
        : Promise.reject(),
    updateObservation: (observationId: string, data: Partial<ObservationFormData>) =>
      activeSession
        ? updateObservation.mutateAsync({ observationId, sessionId: activeSession.id, data })
        : Promise.reject(),
    deleteObservation: (observationId: string) =>
      activeSession
        ? deleteObservation.mutateAsync({ observationId, sessionId: activeSession.id })
        : Promise.reject(),

    // State flags
    isStarting: startSession.isPending,
    isEnding: endSession.isPending,
    isSaving: saveObservation.isPending,
    isUpdating: updateObservation.isPending,
    isDeleting: deleteObservation.isPending,
  };
}
