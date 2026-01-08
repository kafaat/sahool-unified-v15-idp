'use client';

/**
 * Scouting Mode Component
 * مكون وضع الكشافة الحقلية
 *
 * Main scouting interface with:
 * - Toggle to enter/exit scouting mode
 * - Click-on-map to add observation points
 * - Observation form popup
 * - List of current session observations
 * - Session management (start/end)
 */

import React, { useState, useCallback } from 'react';
import { useLocale } from 'next-intl';
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet';
import {
  Eye,
  EyeOff,
  Play,
  Square,
  Plus,
  List,
  AlertCircle,
  Clock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/modal';
import { ObservationForm } from './ObservationForm';
import { ObservationMarker } from './ObservationMarker';
import { useScoutingSessionManager } from '../hooks/useScouting';
import type { GeoPoint, ObservationFormData, Observation } from '../types/scouting';
import { CATEGORY_OPTIONS } from '../types/scouting';
import { clsx } from 'clsx';
import 'leaflet/dist/leaflet.css';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ScoutingModeProps {
  fieldId: string;
  fieldBoundary?: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  center?: [number, number];
  zoom?: number;
}

interface MapClickHandlerProps {
  onMapClick: (latlng: [number, number]) => void;
  enabled: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Map Click Handler Component
// ═══════════════════════════════════════════════════════════════════════════

const MapClickHandler: React.FC<MapClickHandlerProps> = ({ onMapClick, enabled }) => {
  useMapEvents({
    click: (e: any) => {
      if (enabled) {
        onMapClick([e.latlng.lat, e.latlng.lng]);
      }
    },
  });
  return null;
};

// ═══════════════════════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════════════════════

export const ScoutingMode: React.FC<ScoutingModeProps> = ({
  fieldId,
  fieldBoundary: _fieldBoundary,
  center = [24.7136, 46.6753], // Default to Riyadh
  zoom = 15,
}) => {
  const locale = useLocale();
  const isArabic = locale === 'ar';

  // Scouting session manager
  const {
    session,
    observations,
    startSession,
    endSession,
    addObservation,
    deleteObservation,
    isStarting,
    isEnding,
    isSaving,
  } = useScoutingSessionManager(fieldId);

  // UI state
  const [isScoutingMode, setIsScoutingMode] = useState(false);
  const [showObservationForm, setShowObservationForm] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<GeoPoint | null>(null);
  const [showObservationsList, setShowObservationsList] = useState(true);
  const [editingObservation, setEditingObservation] = useState<Observation | null>(null);

  // Check if session is active
  const isSessionActive = session?.status === 'active';

  // ─────────────────────────────────────────────────────────────────────────
  // Handlers
  // ─────────────────────────────────────────────────────────────────────────

  const handleStartSession = async () => {
    try {
      await startSession();
      setIsScoutingMode(true);
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  };

  const handleEndSession = async () => {
    try {
      await endSession();
      setIsScoutingMode(false);
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  };

  const handleMapClick = useCallback(
    (latlng: [number, number]) => {
      if (!isSessionActive || !isScoutingMode) return;

      const location: GeoPoint = {
        type: 'Point',
        coordinates: [latlng[1], latlng[0]], // [lng, lat]
      };

      setSelectedLocation(location);
      setShowObservationForm(true);
    },
    [isSessionActive, isScoutingMode]
  );

  const handleObservationSubmit = async (data: ObservationFormData) => {
    try {
      await addObservation(data);
      setShowObservationForm(false);
      setSelectedLocation(null);
      setEditingObservation(null);
    } catch (error) {
      console.error('Failed to save observation:', error);
    }
  };

  const handleDeleteObservation = async (observationId: string) => {
    if (confirm(isArabic ? 'هل تريد حذف هذه الملاحظة؟' : 'Delete this observation?')) {
      try {
        await deleteObservation(observationId);
      } catch (error) {
        console.error('Failed to delete observation:', error);
      }
    }
  };

  // Calculate session duration
  const sessionDuration = session?.startTime
    ? Math.floor((Date.now() - new Date(session.startTime).getTime()) / 1000 / 60)
    : 0;

  // ─────────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div className="w-full h-full flex flex-col">
      {/* Control Bar */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Session Status */}
            {isSessionActive ? (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-gray-700">
                  {isArabic ? 'جلسة نشطة' : 'Active Session'}
                </span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <Clock className="w-3 h-3 mr-1" />
                  {sessionDuration} {isArabic ? 'دقيقة' : 'min'}
                </Badge>
              </div>
            ) : (
              <span className="text-sm text-gray-600">
                {isArabic ? 'لا توجد جلسة نشطة' : 'No active session'}
              </span>
            )}

            {/* Observations Count */}
            {isSessionActive && (
              <Badge variant="default" className="bg-blue-100 text-blue-800">
                {observations.length} {isArabic ? 'ملاحظة' : 'observations'}
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Scouting Mode Toggle */}
            {isSessionActive && (
              <Button
                size="sm"
                variant={isScoutingMode ? 'primary' : 'outline'}
                onClick={() => setIsScoutingMode(!isScoutingMode)}
              >
                {isScoutingMode ? (
                  <>
                    <Eye className="w-4 h-4 mr-2" />
                    {isArabic ? 'وضع الكشافة نشط' : 'Scouting Active'}
                  </>
                ) : (
                  <>
                    <EyeOff className="w-4 h-4 mr-2" />
                    {isArabic ? 'تفعيل وضع الكشافة' : 'Enable Scouting'}
                  </>
                )}
              </Button>
            )}

            {/* Toggle Observations List */}
            {isSessionActive && observations.length > 0 && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowObservationsList(!showObservationsList)}
              >
                <List className="w-4 h-4 mr-2" />
                {showObservationsList
                  ? isArabic
                    ? 'إخفاء القائمة'
                    : 'Hide List'
                  : isArabic
                  ? 'عرض القائمة'
                  : 'Show List'}
              </Button>
            )}

            {/* Start/End Session */}
            {!isSessionActive ? (
              <Button
                size="sm"
                variant="primary"
                onClick={handleStartSession}
                disabled={isStarting}
              >
                <Play className="w-4 h-4 mr-2" />
                {isStarting
                  ? isArabic
                    ? 'جاري البدء...'
                    : 'Starting...'
                  : isArabic
                  ? 'بدء جلسة كشافة'
                  : 'Start Scouting'}
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                onClick={handleEndSession}
                disabled={isEnding}
                className="text-red-600 hover:bg-red-50 hover:border-red-300"
              >
                <Square className="w-4 h-4 mr-2" />
                {isEnding
                  ? isArabic
                    ? 'جاري الإنهاء...'
                    : 'Ending...'
                  : isArabic
                  ? 'إنهاء الجلسة'
                  : 'End Session'}
              </Button>
            )}
          </div>
        </div>

        {/* Scouting Mode Help Text */}
        {isScoutingMode && isSessionActive && (
          <div className="mt-2 flex items-center gap-2 text-sm text-blue-600 bg-blue-50 px-3 py-2 rounded">
            <AlertCircle className="w-4 h-4" />
            <span>
              {isArabic
                ? 'انقر على الخريطة لإضافة ملاحظة'
                : 'Click on the map to add an observation'}
            </span>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Map */}
        <div className={clsx('flex-1 relative', isScoutingMode && 'cursor-crosshair')}>
          {/* TODO: react-leaflet 4.2.1 types incompatible with React 19 - using type assertion */}
          <MapContainer
            center={center}
            zoom={zoom}
            style={{ width: '100%', height: '100%' }}
            className="z-0"
            {...({} as any)}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              {...({} as any)}
            />

            {/* Map click handler */}
            <MapClickHandler onMapClick={handleMapClick} enabled={isScoutingMode} />

            {/* Observation markers */}
            {observations.map((observation) => (
              <ObservationMarker
                key={observation.id}
                observation={observation}
                onEdit={(obs) => {
                  setEditingObservation(obs);
                  setShowObservationForm(true);
                }}
                onDelete={handleDeleteObservation}
                editable={isSessionActive}
                {...({} as any)}
              />
            ))}
          </MapContainer>

          {/* Map Overlay - Scouting Mode Indicator */}
          {isScoutingMode && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] pointer-events-none">
              <div className="bg-sahool-green-600 text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2">
                <Plus className="w-5 h-5" />
                <span className="font-semibold">
                  {isArabic ? 'انقر لإضافة ملاحظة' : 'Click to add observation'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Observations List Sidebar */}
        {showObservationsList && isSessionActive && observations.length > 0 && (
          <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 mb-3">
                {isArabic ? 'الملاحظات' : 'Observations'}
                <span className="ml-2 text-sm text-gray-600">({observations.length})</span>
              </h3>

              <div className="space-y-3">
                {observations.map((observation) => {
                  const categoryOption = CATEGORY_OPTIONS.find(
                    (opt) => opt.value === observation.category
                  );

                  return (
                    <Card key={observation.id} className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardContent className="p-3">
                        <div className="flex items-start gap-3">
                          <div
                            className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                            style={{ backgroundColor: `${categoryOption?.color}20` }}
                          >
                            <span
                              className="font-bold text-sm"
                              style={{ color: categoryOption?.color }}
                            >
                              {observation.severity}
                            </span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-semibold text-sm text-gray-900">
                              {isArabic ? categoryOption?.labelAr : categoryOption?.label}
                            </p>
                            <p className="text-xs text-gray-600 line-clamp-2 mt-1">
                              {isArabic ? observation.notesAr : observation.notes}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(observation.createdAt).toLocaleTimeString(locale, {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Observation Form Modal */}
      <Modal
        isOpen={showObservationForm}
        onClose={() => {
          setShowObservationForm(false);
          setSelectedLocation(null);
          setEditingObservation(null);
        }}
        title={isArabic ? 'ملاحظة جديدة' : 'New Observation'}
      >
        {selectedLocation && (
          <ObservationForm
            location={selectedLocation}
            onSubmit={handleObservationSubmit}
            onCancel={() => {
              setShowObservationForm(false);
              setSelectedLocation(null);
              setEditingObservation(null);
            }}
            isSubmitting={isSaving}
            initialData={editingObservation ? {
              category: editingObservation.category,
              severity: editingObservation.severity,
              notes: editingObservation.notes,
              // photos are not pre-filled when editing (different types)
            } : undefined}
          />
        )}
      </Modal>
    </div>
  );
};

export default ScoutingMode;
