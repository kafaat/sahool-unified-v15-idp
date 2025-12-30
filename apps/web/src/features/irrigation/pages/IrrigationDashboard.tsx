'use client';

import React from 'react';
import { IrrigationZoneManager } from '../components';

/**
 * Example page demonstrating the IrrigationZoneManager component
 * This page can be used as a standalone dashboard or integrated into a larger farm management system
 */
export default function IrrigationDashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Optional: Add your own header/navigation here */}

      {/* Main Irrigation Zone Manager Component */}
      <IrrigationZoneManager />

      {/* Optional: Add additional components or sections here */}
    </div>
  );
}
