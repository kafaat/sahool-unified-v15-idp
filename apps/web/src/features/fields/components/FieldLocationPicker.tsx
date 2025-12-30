'use client';

/**
 * SAHOOL Field Location Picker Component
 * مكون اختيار موقع الحقل التفاعلي
 *
 * Features:
 * - Interactive Leaflet map for selecting field location
 * - Click to place marker
 * - Search by location name
 * - GPS current location button
 * - Address/coordinate display
 * - Confirm selection button
 * - Arabic labels and RTL support
 *
 * Similar to: John Deere Operations Center location picker
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  MapPin,
  Navigation,
  Search,
  Check,
  X,
  Loader2,
  Globe,
} from 'lucide-react';

// Leaflet type definition for CDN-loaded library
declare global {
  interface Window {
    L?: typeof import('leaflet');
  }
}

interface Location {
  lat: number;
  lng: number;
  address?: string;
}

interface FieldLocationPickerProps {
  onLocationSelect: (location: Location) => void;
  initialLocation?: { lat: number; lng: number };
  height?: string;
}

// Yemen center coordinates
const YEMEN_CENTER: [number, number] = [15.5527, 48.5164];
const DEFAULT_ZOOM = 7;

export const FieldLocationPicker: React.FC<FieldLocationPickerProps> = ({
  onLocationSelect,
  initialLocation,
  height = '500px',
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markerRef = useRef<any>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [mapError, setMapError] = useState<string | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(
    initialLocation ? { ...initialLocation, address: undefined } : null
  );
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [isLoadingAddress, setIsLoadingAddress] = useState(false);

  // Initialize map
  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current) return;

    const initMap = async () => {
      try {
        // Check if Leaflet is loaded
        if (!window.L) {
          await loadLeaflet();
        }

        if (!window.L) {
          setMapError('فشل في تحميل مكتبة الخرائط');
          setIsLoading(false);
          return;
        }

        const L = window.L;

        // Create map if it doesn't exist
        if (!mapInstanceRef.current && mapRef.current) {
          const initialCenter = initialLocation
            ? [initialLocation.lat, initialLocation.lng] as [number, number]
            : YEMEN_CENTER;

          const initialZoom = initialLocation ? 13 : DEFAULT_ZOOM;

          const map = L.map(mapRef.current, {
            zoomControl: true,
          }).setView(initialCenter, initialZoom);

          // Add OpenStreetMap tile layer
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
          }).addTo(map);

          mapInstanceRef.current = map;

          // Add click handler for placing marker
          map.on('click', (e: any) => {
            const { lat, lng } = e.latlng;
            placeMarker(lat, lng);
          });

          // Add initial marker if location provided
          if (initialLocation) {
            placeMarker(initialLocation.lat, initialLocation.lng, false);
          }
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Error initializing map:', error);
        setMapError('حدث خطأ في تحميل الخريطة');
        setIsLoading(false);
      }
    };

    initMap();

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [initialLocation]);

  // Place marker on map
  const placeMarker = useCallback(async (lat: number, lng: number, fetchAddress: boolean = true) => {
    if (!mapInstanceRef.current || !window.L) return;

    const L = window.L;
    const map = mapInstanceRef.current;

    // Remove existing marker
    if (markerRef.current) {
      map.removeLayer(markerRef.current);
    }

    // Create custom icon
    const iconHtml = `
      <div style="
        background-color: #22c55e;
        width: 36px;
        height: 36px;
        border-radius: 50% 50% 50% 0;
        border: 3px solid #ffffff;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transform: rotate(-45deg);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <span style="
          font-size: 18px;
          transform: rotate(45deg);
        ">📍</span>
      </div>
    `;

    const customIcon = L.divIcon({
      html: iconHtml,
      className: 'custom-location-marker',
      iconSize: [36, 36],
      iconAnchor: [18, 36],
    });

    // Add new marker
    const marker = L.marker([lat, lng], { icon: customIcon }).addTo(map);
    markerRef.current = marker;

    // Update selected location
    const location: Location = { lat, lng };

    // Fetch address if needed
    if (fetchAddress) {
      setIsLoadingAddress(true);
      const address = await reverseGeocode(lat, lng);
      location.address = address;
      setIsLoadingAddress(false);
    }

    setSelectedLocation(location);
  }, []);

  // Reverse geocode (get address from coordinates)
  const reverseGeocode = async (lat: number, lng: number): Promise<string | undefined> => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&accept-language=ar`
      );
      const data = await response.json();
      return data.display_name || undefined;
    } catch (error) {
      console.error('Error reverse geocoding:', error);
      return undefined;
    }
  };

  // Search for location
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setShowSearchResults(true);

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          searchQuery
        )}&accept-language=ar&limit=5&countrycodes=ye`
      );
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Error searching location:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Handle search result selection
  const handleSearchResultClick = (result: any) => {
    const lat = parseFloat(result.lat);
    const lng = parseFloat(result.lon);

    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([lat, lng], 15);
      placeMarker(lat, lng, false);

      setSelectedLocation({
        lat,
        lng,
        address: result.display_name,
      });
    }

    setShowSearchResults(false);
    setSearchQuery('');
  };

  // Get current GPS location
  const handleGetCurrentLocation = () => {
    if (!('geolocation' in navigator)) {
      alert('المتصفح لا يدعم تحديد الموقع');
      return;
    }

    setIsGettingLocation(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;

        if (mapInstanceRef.current) {
          mapInstanceRef.current.setView([latitude, longitude], 15);
          placeMarker(latitude, longitude);
        }

        setIsGettingLocation(false);
      },
      (error) => {
        console.error('Error getting location:', error);
        alert('تعذر الحصول على الموقع الحالي. تأكد من منح الإذن لتحديد الموقع.');
        setIsGettingLocation(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  };

  // Confirm location selection
  const handleConfirm = () => {
    if (selectedLocation) {
      onLocationSelect(selectedLocation);
    }
  };

  // Clear selection
  const handleClear = () => {
    if (markerRef.current && mapInstanceRef.current) {
      mapInstanceRef.current.removeLayer(markerRef.current);
      markerRef.current = null;
    }
    setSelectedLocation(null);
  };

  // Handle search input key press
  const handleSearchKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div
        className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative flex items-center justify-center"
        style={{ height }}
      >
        <div className="flex flex-col items-center">
          <Loader2 className="w-10 h-10 animate-spin text-green-600 mb-3" />
          <p className="text-gray-600">جاري تحميل الخريطة...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (mapError) {
    return (
      <div
        className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative flex items-center justify-center"
        style={{ height }}
      >
        <div className="flex flex-col items-center text-center p-4">
          <MapPin className="w-12 h-12 text-gray-400 mb-3" />
          <p className="text-gray-600 font-medium">{mapError}</p>
          <p className="text-sm text-gray-500 mt-1">يرجى التحقق من اتصال الإنترنت</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="bg-white rounded-xl border border-gray-200 overflow-hidden relative shadow-sm"
      style={{ height }}
    >
      {/* Map Container */}
      <div ref={mapRef} className="w-full h-full" />

      {/* Search Bar */}
      <div className="absolute top-4 left-4 right-4 z-[1000]">
        <div className="max-w-md mx-auto">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleSearchKeyPress}
              onFocus={() => searchResults.length > 0 && setShowSearchResults(true)}
              placeholder="ابحث عن موقع..."
              className="w-full px-4 py-3 pr-12 rounded-lg border border-gray-300 bg-white shadow-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-right"
              dir="rtl"
            />
            <button
              onClick={handleSearch}
              disabled={isSearching || !searchQuery.trim()}
              className="absolute left-2 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSearching ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
            </button>
          </div>

          {/* Search Results */}
          {showSearchResults && searchResults.length > 0 && (
            <div className="mt-2 bg-white rounded-lg border border-gray-300 shadow-lg max-h-64 overflow-y-auto">
              {searchResults.map((result, index) => (
                <button
                  key={index}
                  onClick={() => handleSearchResultClick(result)}
                  className="w-full px-4 py-3 text-right hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
                >
                  <div className="flex items-start gap-2" dir="rtl">
                    <MapPin className="w-4 h-4 text-green-600 mt-1 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{result.display_name}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Control Buttons */}
      <div className="absolute top-20 left-4 z-[1000] flex flex-col gap-2">
        {/* GPS Location Button */}
        <button
          onClick={handleGetCurrentLocation}
          disabled={isGettingLocation}
          className="bg-white rounded-lg shadow-lg p-3 text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="موقعي الحالي"
        >
          {isGettingLocation ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Navigation className="w-5 h-5" />
          )}
        </button>

        {/* Map Type Button */}
        <button
          className="bg-white rounded-lg shadow-lg p-3 text-gray-700 hover:bg-gray-50 transition-colors"
          title="نوع الخريطة"
        >
          <Globe className="w-5 h-5" />
        </button>
      </div>

      {/* Location Info Panel */}
      {selectedLocation && (
        <div className="absolute bottom-4 left-4 right-4 z-[1000]">
          <div className="max-w-2xl mx-auto bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-4">
            <div className="flex items-start justify-between gap-4" dir="rtl">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <h3 className="font-semibold text-gray-900">الموقع المحدد</h3>
                </div>

                {/* Coordinates */}
                <div className="space-y-1 text-sm text-gray-600 mb-2">
                  <div className="flex gap-4">
                    <span>
                      <span className="font-medium">خط العرض:</span> {selectedLocation.lat.toFixed(6)}
                    </span>
                    <span>
                      <span className="font-medium">خط الطول:</span> {selectedLocation.lng.toFixed(6)}
                    </span>
                  </div>
                </div>

                {/* Address */}
                {isLoadingAddress ? (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>جاري تحميل العنوان...</span>
                  </div>
                ) : selectedLocation.address ? (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">العنوان:</span> {selectedLocation.address}
                  </div>
                ) : null}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 flex-shrink-0">
                <button
                  onClick={handleConfirm}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 shadow-md"
                >
                  <Check className="w-4 h-4" />
                  <span className="text-sm font-medium">تأكيد</span>
                </button>
                <button
                  onClick={handleClear}
                  className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
                >
                  <X className="w-4 h-4" />
                  <span className="text-sm font-medium">إلغاء</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Instructions Overlay */}
      {!selectedLocation && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-[1000]">
          <div className="bg-white/95 backdrop-blur-sm rounded-lg shadow-lg px-4 py-2">
            <p className="text-sm text-gray-600 text-center" dir="rtl">
              انقر على الخريطة لتحديد موقع الحقل أو استخدم البحث
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function to load Leaflet dynamically
async function loadLeaflet(): Promise<void> {
  return new Promise((resolve, reject) => {
    // Check if already loaded
    if (window.L) {
      resolve();
      return;
    }

    // Load CSS
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    cssLink.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTlZBo=';
    cssLink.crossOrigin = '';
    document.head.appendChild(cssLink);

    // Load JS
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    script.crossOrigin = '';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Leaflet'));
    document.head.appendChild(script);
  });
}

export default FieldLocationPicker;
