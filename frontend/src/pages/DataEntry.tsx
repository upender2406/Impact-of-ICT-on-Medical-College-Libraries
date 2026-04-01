import { Questionnaire } from '@/components/forms/Questionnaire';
import { BulkImport } from '@/components/forms/BulkImport';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useQueryClient } from '@tanstack/react-query';
import { FileText, Upload } from 'lucide-react';

export function DataEntry() {
  const [activeForm, setActiveForm] = useState<'comprehensive' | 'bulk'>('comprehensive');
  const queryClient = useQueryClient();

  // Callback to invalidate queries after successful submission
  const handleSubmitSuccess = () => {
    // Invalidate all data queries to trigger refresh
    queryClient.invalidateQueries({ queryKey: ['responses'] });
    queryClient.invalidateQueries({ queryKey: ['summary'] });
    queryClient.invalidateQueries({ queryKey: ['training-status'] });
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Data Entry</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Submit ICT infrastructure and satisfaction survey data
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant={activeForm === 'comprehensive' ? 'default' : 'outline'}
            onClick={() => setActiveForm('comprehensive')}
          >
            <FileText className="mr-2 h-4 w-4" />
            Comprehensive Survey
          </Button>
          <Button
            variant={activeForm === 'bulk' ? 'default' : 'outline'}
            onClick={() => setActiveForm('bulk')}
          >
            <Upload className="mr-2 h-4 w-4" />
            Quick Import
          </Button>
        </div>
      </div>

      {/* Form Description */}
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            {activeForm === 'comprehensive' && <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />}
            {activeForm === 'bulk' && <Upload className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />}
          </div>
          <div>
            <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-1">
              {activeForm === 'comprehensive' && 'Comprehensive Survey'}
              {activeForm === 'bulk' && 'Quick Import'}
            </h3>
            <p className="text-sm text-blue-800 dark:text-blue-400">
              {activeForm === 'comprehensive' && 'Complete survey with all infrastructure, satisfaction, and barrier assessments. Fill out the form manually with detailed information.'}
              {activeForm === 'bulk' && 'Upload Excel or CSV files to import multiple survey responses at once. Perfect for batch data processing.'}
            </p>
          </div>
        </div>
      </div>

      {/* Render appropriate form */}
      {activeForm === 'comprehensive' ? (
        <Questionnaire 
          onSuccess={handleSubmitSuccess} 
          mode="comprehensive"
        />
      ) : (
        <BulkImport onSuccess={handleSubmitSuccess} />
      )}
    </div>
  );
}
