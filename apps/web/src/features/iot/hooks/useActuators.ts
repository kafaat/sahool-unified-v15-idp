/**
 * IoT Actuators - React Hooks
 * خطافات React للمُشغلات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { actuatorsApi, alertRulesApi } from '../api';

// Query Keys
export const actuatorKeys = {
  all: ['actuators'] as const,
  lists: () => [...actuatorKeys.all, 'list'] as const,
  list: (fieldId?: string) => [...actuatorKeys.lists(), fieldId] as const,
  detail: (id: string) => [...actuatorKeys.all, 'detail', id] as const,
};

export const alertRuleKeys = {
  all: ['alertRules'] as const,
  lists: () => [...alertRuleKeys.all, 'list'] as const,
  list: (sensorId?: string) => [...alertRuleKeys.lists(), sensorId] as const,
  detail: (id: string) => [...alertRuleKeys.all, 'detail', id] as const,
};

/**
 * Hook to fetch actuators list
 */
export function useActuators(fieldId?: string) {
  return useQuery({
    queryKey: actuatorKeys.list(fieldId),
    queryFn: () => actuatorsApi.getActuators(fieldId),
    staleTime: 1000 * 30, // 30 seconds
    refetchInterval: 1000 * 60, // Refetch every minute
  });
}

/**
 * Hook to fetch single actuator
 */
export function useActuator(id: string) {
  return useQuery({
    queryKey: actuatorKeys.detail(id),
    queryFn: () => actuatorsApi.getActuatorById(id),
    enabled: !!id,
  });
}

/**
 * Hook to control actuator
 */
export function useControlActuator() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ActuatorControlData) => actuatorsApi.controlActuator(data),
    onSuccess: (updatedActuator) => {
      queryClient.invalidateQueries({ queryKey: actuatorKeys.lists() });
      queryClient.setQueryData(actuatorKeys.detail(updatedActuator.id), updatedActuator);
    },
  });
}

/**
 * Hook to set actuator mode
 */
export function useSetActuatorMode() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      actuatorId,
      mode,
    }: {
      actuatorId: string;
      mode: 'manual' | 'automatic' | 'scheduled';
    }) => actuatorsApi.setMode(actuatorId, mode),
    onSuccess: (updatedActuator) => {
      queryClient.invalidateQueries({ queryKey: actuatorKeys.lists() });
      queryClient.setQueryData(actuatorKeys.detail(updatedActuator.id), updatedActuator);
    },
  });
}

/**
 * Hook to fetch alert rules
 */
export function useAlertRules(sensorId?: string) {
  return useQuery({
    queryKey: alertRuleKeys.list(sensorId),
    queryFn: () => alertRulesApi.getAlertRules(sensorId),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch single alert rule
 */
export function useAlertRule(id: string) {
  return useQuery({
    queryKey: alertRuleKeys.detail(id),
    queryFn: () => alertRulesApi.getAlertRuleById(id),
    enabled: !!id,
  });
}

/**
 * Hook to create alert rule
 */
export function useCreateAlertRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AlertRuleFormData) => alertRulesApi.createAlertRule(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertRuleKeys.lists() });
    },
  });
}

/**
 * Hook to update alert rule
 */
export function useUpdateAlertRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<AlertRuleFormData> }) =>
      alertRulesApi.updateAlertRule(id, data),
    onSuccess: (updatedRule) => {
      queryClient.invalidateQueries({ queryKey: alertRuleKeys.lists() });
      queryClient.setQueryData(alertRuleKeys.detail(updatedRule.id), updatedRule);
    },
  });
}

/**
 * Hook to delete alert rule
 */
export function useDeleteAlertRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => alertRulesApi.deleteAlertRule(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: alertRuleKeys.lists() });
      queryClient.removeQueries({ queryKey: alertRuleKeys.detail(id) });
    },
  });
}

/**
 * Hook to toggle alert rule
 */
export function useToggleAlertRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      alertRulesApi.toggleAlertRule(id, enabled),
    onSuccess: (updatedRule) => {
      queryClient.invalidateQueries({ queryKey: alertRuleKeys.lists() });
      queryClient.setQueryData(alertRuleKeys.detail(updatedRule.id), updatedRule);
    },
  });
}
