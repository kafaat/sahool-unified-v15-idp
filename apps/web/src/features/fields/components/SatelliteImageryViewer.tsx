'use client';

/**
 * SAHOOL Satellite Imagery Viewer Component
 * مكون عرض صور الأقمار الصناعية
 *
 * Similar to: Farmonaut, Climate FieldView, Planet Labs
 *
 * Features:
 * - Multi-spectral imagery display
 * - NDVI, NDWI, EVI index visualization
 * - Time series comparison
 * - Cloud cover indicator
 * - Image download
 */

import React, { useState, useCallback } from 'react';
import {
  Layers,
  Calendar,
  Download,
  RefreshCw,
  Cloud,
  Sun,
  Eye,
  TrendingUp,
  Droplets,
  Leaf,
} from 'lucide-react';

// Vegetation index types
type VegetationIndex = 'NDVI' | 'NDWI' | 'EVI' | 'SAVI' | 'GNDVI' | 'RGB';

interface SatelliteImage {
  id: string;
  date: string;
  source: 'Sentinel-2' | 'Landsat-8' | 'Planet';
  cloudCover: number;
  thumbnail?: string;
  indices: {
    ndvi?: number;
    ndwi?: number;
    evi?: number;
    savi?: number;
  };
}

interface SatelliteImageryViewerProps {
  fieldId: string;
  fieldName?: string;
  images?: SatelliteImage[];
  onIndexSelect?: (index: VegetationIndex) => void;
  onDateSelect?: (date: string) => void;
  onImageDownload?: (imageId: string, index: VegetationIndex) => void;
  isLoading?: boolean;
}

// Index color scales
const INDEX_COLORS: Record<VegetationIndex, { low: string; mid: string; high: string; label: string; labelAr: string }> = {
  NDVI: { low: '#d73027', mid: '#fee08b', high: '#1a9850', label: 'Vegetation Health', labelAr: 'صحة النبات' },
  NDWI: { low: '#d73027', mid: '#fee08b', high: '#4575b4', label: 'Water Content', labelAr: 'محتوى المياه' },
  EVI: { low: '#d73027', mid: '#fee08b', high: '#006837', label: 'Enhanced Vegetation', labelAr: 'الغطاء النباتي المحسن' },
  SAVI: { low: '#8c510a', mid: '#f6e8c3', high: '#01665e', label: 'Soil Adjusted', labelAr: 'تعديل التربة' },
  GNDVI: { low: '#d73027', mid: '#ffffbf', high: '#1a9850', label: 'Green NDVI', labelAr: 'NDVI الأخضر' },
  RGB: { low: '#000', mid: '#888', high: '#fff', label: 'True Color', labelAr: 'اللون الحقيقي' },
};

// Mock satellite images for demo
const MOCK_IMAGES: SatelliteImage[] = [
  {
    id: '1',
    date: '2024-12-28',
    source: 'Sentinel-2',
    cloudCover: 5,
    indices: { ndvi: 0.72, ndwi: 0.45, evi: 0.68 },
  },
  {
    id: '2',
    date: '2024-12-23',
    source: 'Sentinel-2',
    cloudCover: 12,
    indices: { ndvi: 0.68, ndwi: 0.42, evi: 0.64 },
  },
  {
    id: '3',
    date: '2024-12-18',
    source: 'Sentinel-2',
    cloudCover: 8,
    indices: { ndvi: 0.65, ndwi: 0.38, evi: 0.61 },
  },
  {
    id: '4',
    date: '2024-12-13',
    source: 'Landsat-8',
    cloudCover: 3,
    indices: { ndvi: 0.70, ndwi: 0.44, evi: 0.66 },
  },
];

// Get color for index value
const getIndexColor = (index: VegetationIndex, value: number): string => {
  const colors = INDEX_COLORS[index];
  if (value < 0.3) return colors.low;
  if (value < 0.6) return colors.mid;
  return colors.high;
};

// Format date in Arabic
const formatDateAr = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ar-YE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const SatelliteImageryViewer: React.FC<SatelliteImageryViewerProps> = ({
  fieldId: _fieldId,
  fieldName = 'الحقل',
  images = MOCK_IMAGES,
  onIndexSelect,
  onDateSelect,
  onImageDownload,
  isLoading = false,
}) => {
  void _fieldId; // Reserved for API calls
  const [selectedIndex, setSelectedIndex] = useState<VegetationIndex>('NDVI');
  const [selectedImageId, setSelectedImageId] = useState<string>(images[0]?.id || '');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const selectedImage = images.find((img) => img.id === selectedImageId) || images[0];

  // Handle index change
  const handleIndexChange = useCallback((index: VegetationIndex) => {
    setSelectedIndex(index);
    onIndexSelect?.(index);
  }, [onIndexSelect]);

  // Handle image selection
  const handleImageSelect = useCallback((imageId: string) => {
    setSelectedImageId(imageId);
    const image = images.find((img) => img.id === imageId);
    if (image) {
      onDateSelect?.(image.date);
    }
  }, [images, onDateSelect]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    setIsRefreshing(true);
    // Simulate refresh
    setTimeout(() => setIsRefreshing(false), 2000);
  }, []);

  // Handle download
  const handleDownload = useCallback(() => {
    if (selectedImage) {
      onImageDownload?.(selectedImage.id, selectedIndex);
    }
  }, [selectedImage, selectedIndex, onImageDownload]);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-green-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-gray-900">صور الأقمار الصناعية</h3>
            <span className="text-sm text-gray-500">- {fieldName}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="تحديث الصور"
            >
              <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={handleDownload}
              className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="تحميل الصورة"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Index Selector */}
      <div className="p-4 border-b border-gray-100 bg-gray-50">
        <div className="flex flex-wrap gap-2">
          {(Object.keys(INDEX_COLORS) as VegetationIndex[]).map((index) => {
            const isSelected = selectedIndex === index;

            return (
              <button
                key={index}
                onClick={() => handleIndexChange(index)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isSelected
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-700 hover:border-blue-300'
                }`}
              >
                {index === 'NDVI' && <Leaf className="w-4 h-4" />}
                {index === 'NDWI' && <Droplets className="w-4 h-4" />}
                {index === 'EVI' && <TrendingUp className="w-4 h-4" />}
                {index === 'RGB' && <Eye className="w-4 h-4" />}
                <span>{index}</span>
              </button>
            );
          })}
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {INDEX_COLORS[selectedIndex].labelAr} - {INDEX_COLORS[selectedIndex].label}
        </p>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4">
        {/* Image Display */}
        <div className="lg:col-span-2">
          <div className="relative aspect-video bg-gray-100 rounded-xl overflow-hidden">
            {isLoading ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <RefreshCw className="w-8 h-8 text-gray-400 animate-spin" />
              </div>
            ) : (
              <>
                {/* Placeholder for satellite image */}
                <div
                  className="absolute inset-0"
                  style={{
                    background: `linear-gradient(135deg, ${INDEX_COLORS[selectedIndex].low} 0%, ${INDEX_COLORS[selectedIndex].mid} 50%, ${INDEX_COLORS[selectedIndex].high} 100%)`,
                    opacity: 0.7,
                  }}
                />

                {/* Field overlay simulation */}
                <div className="absolute inset-4 border-2 border-white/50 rounded-lg" />

                {/* Index value overlay */}
                {selectedImage && selectedImage.indices[selectedIndex.toLowerCase() as keyof typeof selectedImage.indices] && (
                  <div className="absolute top-4 right-4 bg-black/70 text-white px-3 py-2 rounded-lg">
                    <div className="text-xs opacity-70">{selectedIndex}</div>
                    <div className="text-2xl font-bold">
                      {(selectedImage.indices[selectedIndex.toLowerCase() as keyof typeof selectedImage.indices] ?? 0).toFixed(2)}
                    </div>
                  </div>
                )}

                {/* Date overlay */}
                {selectedImage && (
                  <div className="absolute bottom-4 left-4 bg-black/70 text-white px-3 py-2 rounded-lg">
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDateAr(selectedImage.date)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs opacity-70 mt-1">
                      <Cloud className="w-3 h-3" />
                      <span>غطاء سحابي: {selectedImage.cloudCover}%</span>
                    </div>
                  </div>
                )}

                {/* Source badge */}
                {selectedImage && (
                  <div className="absolute top-4 left-4 bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium">
                    {selectedImage.source}
                  </div>
                )}
              </>
            )}
          </div>

          {/* Color Legend */}
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className="w-32 h-3 rounded-full"
                style={{
                  background: `linear-gradient(to right, ${INDEX_COLORS[selectedIndex].low}, ${INDEX_COLORS[selectedIndex].mid}, ${INDEX_COLORS[selectedIndex].high})`,
                }}
              />
            </div>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>منخفض</span>
              <span>متوسط</span>
              <span>مرتفع</span>
            </div>
          </div>
        </div>

        {/* Image Timeline */}
        <div className="lg:col-span-1">
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            الصور المتاحة
          </h4>

          <div className="space-y-2 max-h-80 overflow-y-auto">
            {images.map((image) => {
              const isSelected = image.id === selectedImageId;
              const indexValue = image.indices[selectedIndex.toLowerCase() as keyof typeof image.indices];

              return (
                <button
                  key={image.id}
                  onClick={() => handleImageSelect(image.id)}
                  className={`w-full p-3 rounded-lg border text-right transition-colors ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">{image.source}</span>
                    <div className="flex items-center gap-1">
                      {image.cloudCover < 10 ? (
                        <Sun className="w-3 h-3 text-yellow-500" />
                      ) : (
                        <Cloud className="w-3 h-3 text-gray-400" />
                      )}
                      <span className="text-xs text-gray-500">{image.cloudCover}%</span>
                    </div>
                  </div>

                  <div className="text-sm font-medium text-gray-900">
                    {formatDateAr(image.date)}
                  </div>

                  {indexValue !== undefined && (
                    <div className="flex items-center gap-2 mt-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: getIndexColor(selectedIndex, indexValue) }}
                      />
                      <span className="text-xs text-gray-600">
                        {selectedIndex}: {indexValue.toFixed(2)}
                      </span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Stats Summary */}
          {images.length > 0 && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <h5 className="text-xs font-medium text-gray-500 mb-2">ملخص الفترة</h5>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-500">أعلى قيمة:</span>
                  <span className="font-medium text-gray-900 mr-1">
                    {Math.max(...images.map((img) => img.indices[selectedIndex.toLowerCase() as keyof typeof img.indices] || 0)).toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">أقل قيمة:</span>
                  <span className="font-medium text-gray-900 mr-1">
                    {Math.min(...images.map((img) => img.indices[selectedIndex.toLowerCase() as keyof typeof img.indices] || 1)).toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">المتوسط:</span>
                  <span className="font-medium text-gray-900 mr-1">
                    {(images.reduce((sum, img) => sum + (img.indices[selectedIndex.toLowerCase() as keyof typeof img.indices] || 0), 0) / images.length).toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">عدد الصور:</span>
                  <span className="font-medium text-gray-900 mr-1">{images.length}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SatelliteImageryViewer;
