'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Feedback Components Usage Examples
// Comprehensive examples for all feedback and notification components
// ═══════════════════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { ToastProvider, useToast } from './ModernToast';
import { ModernAlert } from './ModernAlert';
import { ModernBadge } from './ModernBadge';
import { ModernProgress, CircularProgress } from './ModernProgress';
import { ModernSpinner, SpinnerOverlay } from './ModernSpinner';
import { ConfirmDialog } from './ConfirmDialog';
import { Bell, Mail, Star, Trash2, Save } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════════
// Toast Examples
// ═══════════════════════════════════════════════════════════════════════════════

function ToastExamples() {
  const toast = useToast();

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
        Toast Notifications
      </h3>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => toast.success('Success!', 'Your action was completed successfully.')}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Show Success Toast
        </button>

        <button
          onClick={() => toast.error('Error!', 'Something went wrong. Please try again.')}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Show Error Toast
        </button>

        <button
          onClick={() => toast.warning('Warning!', 'This action cannot be undone.')}
          className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
        >
          Show Warning Toast
        </button>

        <button
          onClick={() => toast.info('Information', 'Here is some useful information for you.')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Show Info Toast
        </button>

        <button
          onClick={() => {
            toast.addToast({
              title: 'Custom Duration',
              description: 'This toast will stay for 10 seconds',
              variant: 'info',
              duration: 10000,
            });
          }}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Long Duration Toast
        </button>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Examples
// ═══════════════════════════════════════════════════════════════════════════════

function AlertExamples() {
  const [showAlert, setShowAlert] = useState(true);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
        Alert Banners
      </h3>

      <div className="space-y-3">
        <ModernAlert
          variant="success"
          title="Congratulations!"
          description="Your profile has been updated successfully."
          dismissible
        />

        <ModernAlert
          variant="error"
          title="Authentication Error"
          description="Invalid credentials. Please check your username and password."
          dismissible
        />

        <ModernAlert
          variant="warning"
          title="Maintenance Scheduled"
          description="The system will undergo maintenance on Sunday at 2 AM."
          dismissible
        />

        <ModernAlert
          variant="info"
          title="New Feature Available"
          dismissible
        >
          <p className="mb-2">
            We have just released a new feature that allows you to export your data.
          </p>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>Export to CSV, JSON, or PDF</li>
            <li>Schedule automatic exports</li>
            <li>Share exports with team members</li>
          </ul>
        </ModernAlert>

        <ModernAlert
          variant="info"
          title="Take Action"
          description="Complete your profile to unlock all features."
          actions={
            <>
              <button className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
                Complete Profile
              </button>
              <button className="px-3 py-1.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600">
                Remind Me Later
              </button>
            </>
          }
        />

        {showAlert && (
          <ModernAlert
            variant="success"
            title="Dismissible Alert"
            description="Click the X button to dismiss this alert."
            dismissible
            onDismiss={() => setShowAlert(false)}
          />
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Badge Examples
// ═══════════════════════════════════════════════════════════════════════════════

function BadgeExamples() {
  const [notificationCount, setNotificationCount] = useState(5);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white">Badges</h3>

      <div className="space-y-6">
        {/* Variants */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Variants
          </h4>
          <div className="flex flex-wrap gap-2">
            <ModernBadge variant="primary">Primary</ModernBadge>
            <ModernBadge variant="success">Success</ModernBadge>
            <ModernBadge variant="warning">Warning</ModernBadge>
            <ModernBadge variant="danger">Danger</ModernBadge>
            <ModernBadge variant="info">Info</ModernBadge>
            <ModernBadge variant="neutral">Neutral</ModernBadge>
          </div>
        </div>

        {/* Sizes */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Sizes
          </h4>
          <div className="flex items-center flex-wrap gap-2">
            <ModernBadge size="sm">Small</ModernBadge>
            <ModernBadge size="md">Medium</ModernBadge>
            <ModernBadge size="lg">Large</ModernBadge>
          </div>
        </div>

        {/* With Icons */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            With Icons
          </h4>
          <div className="flex flex-wrap gap-2">
            <ModernBadge variant="primary" icon={Bell}>
              Notifications
            </ModernBadge>
            <ModernBadge variant="success" icon={Mail}>
              Messages
            </ModernBadge>
            <ModernBadge variant="warning" icon={Star}>
              Premium
            </ModernBadge>
          </div>
        </div>

        {/* With Pulse */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Pulse Animation
          </h4>
          <div className="flex flex-wrap gap-2">
            <ModernBadge variant="danger" pulse>
              Live
            </ModernBadge>
            <ModernBadge variant="success" pulse dot>
              Online
            </ModernBadge>
            <ModernBadge variant="warning" pulse dot>
              Away
            </ModernBadge>
          </div>
        </div>

        {/* Outline Style */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Outline Style
          </h4>
          <div className="flex flex-wrap gap-2">
            <ModernBadge variant="primary" outline>
              Primary
            </ModernBadge>
            <ModernBadge variant="success" outline>
              Success
            </ModernBadge>
            <ModernBadge variant="danger" outline>
              Danger
            </ModernBadge>
          </div>
        </div>

        {/* Pill Shape */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Pill Shape
          </h4>
          <div className="flex flex-wrap gap-2">
            <ModernBadge variant="primary" pill>
              New
            </ModernBadge>
            <ModernBadge variant="success" pill>
              Active
            </ModernBadge>
            <ModernBadge variant="danger" pill>
              Hot
            </ModernBadge>
          </div>
        </div>

        {/* Interactive */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Interactive Badge
          </h4>
          <div className="flex items-center gap-3">
            <div className="relative inline-flex">
              <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg">
                Notifications
              </button>
              <ModernBadge
                variant="danger"
                size="sm"
                pill
                className="absolute -top-2 -right-2"
              >
                {notificationCount}
              </ModernBadge>
            </div>
            <ModernBadge
              variant="danger"
              onClick={() => setNotificationCount(Math.max(0, notificationCount - 1))}
              pill
            >
              Clear {notificationCount}
            </ModernBadge>
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Progress Examples
// ═══════════════════════════════════════════════════════════════════════════════

function ProgressExamples() {
  const [progress, setProgress] = useState(45);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
        Progress Indicators
      </h3>

      <div className="space-y-6">
        {/* Linear Progress */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Linear Progress
          </h4>
          <div className="space-y-3">
            <ModernProgress value={progress} showLabel label="Upload Progress" />
            <ModernProgress value={75} variant="success" showLabel label="Success" />
            <ModernProgress value={50} variant="warning" showLabel label="Warning" />
            <ModernProgress value={30} variant="danger" showLabel label="Danger" />
            <ModernProgress value={85} variant="gradient" showLabel label="Gradient" glow />
          </div>
        </div>

        {/* Sizes */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Sizes
          </h4>
          <div className="space-y-3">
            <ModernProgress value={60} size="sm" />
            <ModernProgress value={60} size="md" />
            <ModernProgress value={60} size="lg" />
          </div>
        </div>

        {/* Striped & Animated */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Striped & Animated
          </h4>
          <ModernProgress value={70} variant="primary" striped showLabel />
        </div>

        {/* Indeterminate */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Indeterminate (Loading)
          </h4>
          <ModernProgress value={0} indeterminate label="Processing..." />
        </div>

        {/* Circular Progress */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Circular Progress
          </h4>
          <div className="flex items-center gap-6">
            <CircularProgress value={progress} showLabel />
            <CircularProgress value={75} variant="success" showLabel size={80} />
            <CircularProgress value={50} variant="warning" showLabel size={96} strokeWidth={8} />
            <CircularProgress value={30} variant="danger" showLabel />
          </div>
        </div>

        {/* Control */}
        <div className="flex gap-2">
          <button
            onClick={() => setProgress(Math.max(0, progress - 10))}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg"
          >
            -10%
          </button>
          <button
            onClick={() => setProgress(Math.min(100, progress + 10))}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg"
          >
            +10%
          </button>
          <button
            onClick={() => setProgress(0)}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg"
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Spinner Examples
// ═══════════════════════════════════════════════════════════════════════════════

function SpinnerExamples() {
  const [showOverlay, setShowOverlay] = useState(false);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
        Loading Spinners
      </h3>

      <div className="space-y-6">
        {/* Variants */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Variants
          </h4>
          <div className="flex flex-wrap items-center gap-6">
            <ModernSpinner variant="dots" />
            <ModernSpinner variant="ring" />
            <ModernSpinner variant="bars" />
            <ModernSpinner variant="pulse" />
            <ModernSpinner variant="bounce" />
            <ModernSpinner variant="gradient" />
          </div>
        </div>

        {/* Sizes */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Sizes
          </h4>
          <div className="flex items-center gap-4">
            <ModernSpinner size="sm" />
            <ModernSpinner size="md" />
            <ModernSpinner size="lg" />
            <ModernSpinner size="xl" />
          </div>
        </div>

        {/* Colors */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Colors
          </h4>
          <div className="flex flex-wrap gap-4">
            <ModernSpinner color="primary" />
            <ModernSpinner color="success" />
            <ModernSpinner color="warning" />
            <ModernSpinner color="danger" />
            <ModernSpinner color="gray" />
            <div className="bg-gray-800 p-4 rounded-lg">
              <ModernSpinner color="white" />
            </div>
          </div>
        </div>

        {/* In Buttons */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            In Buttons
          </h4>
          <div className="flex gap-2">
            <button className="px-4 py-2 bg-sahool-600 text-white rounded-lg flex items-center gap-2">
              <ModernSpinner size="sm" color="white" variant="dots" />
              Loading...
            </button>
            <button className="px-4 py-2 bg-green-600 text-white rounded-lg flex items-center gap-2">
              <ModernSpinner size="sm" color="white" variant="ring" />
              Processing
            </button>
          </div>
        </div>

        {/* Overlay */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Full Page Overlay
          </h4>
          <button
            onClick={() => {
              setShowOverlay(true);
              setTimeout(() => setShowOverlay(false), 3000);
            }}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg"
          >
            Show Loading Overlay (3s)
          </button>
          <SpinnerOverlay
            visible={showOverlay}
            variant="gradient"
            message="Loading your content..."
          />
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Dialog Examples
// ═══════════════════════════════════════════════════════════════════════════════

function DialogExamples() {
  const [showDialog, setShowDialog] = useState(false);
  const [dialogVariant, setDialogVariant] = useState<'info' | 'warning' | 'danger' | 'success'>('info');
  const [isDeleting, setIsDeleting] = useState(false);
  const toast = useToast();

  const handleDelete = async () => {
    setIsDeleting(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsDeleting(false);
    toast.success('Deleted', 'Item has been deleted successfully');
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
        Confirmation Dialogs
      </h3>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => {
            setDialogVariant('info');
            setShowDialog(true);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg"
        >
          Info Dialog
        </button>

        <button
          onClick={() => {
            setDialogVariant('warning');
            setShowDialog(true);
          }}
          className="px-4 py-2 bg-yellow-600 text-white rounded-lg"
        >
          Warning Dialog
        </button>

        <button
          onClick={() => {
            setDialogVariant('danger');
            setShowDialog(true);
          }}
          className="px-4 py-2 bg-red-600 text-white rounded-lg"
        >
          Danger Dialog
        </button>

        <button
          onClick={() => {
            setDialogVariant('success');
            setShowDialog(true);
          }}
          className="px-4 py-2 bg-green-600 text-white rounded-lg"
        >
          Success Dialog
        </button>
      </div>

      <ConfirmDialog
        open={showDialog}
        onClose={() => setShowDialog(false)}
        onConfirm={async () => {
          if (dialogVariant === 'danger') {
            await handleDelete();
          } else {
            toast.success('Confirmed', 'Action has been confirmed');
          }
        }}
        variant={dialogVariant}
        title={
          dialogVariant === 'info' ? 'Information' :
          dialogVariant === 'warning' ? 'Are you sure?' :
          dialogVariant === 'danger' ? 'Delete Item?' :
          'Success!'
        }
        description={
          dialogVariant === 'info' ? 'This is an informational dialog to notify you about something important.' :
          dialogVariant === 'warning' ? 'This action may have consequences. Please review before proceeding.' :
          dialogVariant === 'danger' ? 'This action cannot be undone. This will permanently delete the item.' :
          'Your action has been completed successfully!'
        }
        confirmLabel={
          dialogVariant === 'danger' ? 'Delete' :
          dialogVariant === 'warning' ? 'Proceed' :
          'Confirm'
        }
        loading={isDeleting}
      >
        {dialogVariant === 'danger' && (
          <div className="mt-3 p-3 bg-red-50 dark:bg-red-950/30 rounded-lg border border-red-200 dark:border-red-800">
            <p className="text-sm text-red-800 dark:text-red-200">
              Type <strong>DELETE</strong> to confirm this action.
            </p>
          </div>
        )}
      </ConfirmDialog>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Main Example Component
// ═══════════════════════════════════════════════════════════════════════════════

export function FeedbackComponentsExample() {
  return (
    <ToastProvider position="top-right">
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Feedback & Notification Components
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Modern, accessible components for user feedback and notifications
            </p>
          </div>

          <div className="space-y-12">
            <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
              <ToastExamples />
            </section>

            <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
              <AlertExamples />
            </section>

            <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
              <BadgeExamples />
            </section>

            <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
              <ProgressExamples />
            </section>

            <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
              <SpinnerExamples />
            </section>

            <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
              <DialogExamples />
            </section>
          </div>
        </div>
      </div>
    </ToastProvider>
  );
}

export default FeedbackComponentsExample;
