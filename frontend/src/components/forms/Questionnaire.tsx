import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Select } from '@/components/ui/select';
import { COLLEGES, AUTOMATION_SYSTEMS, INFRASTRUCTURE_LABELS } from '@/lib/constants';
import type { SurveyResponse, InfrastructureAssessment, ServiceQuality, BarriersAssessment, AdditionalInfo, Respondent } from '@/types';
import { Save, ArrowRight, ArrowLeft, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/lib/api';
import toast from 'react-hot-toast';

interface FormData {
  collegeId: string;
  respondent: Respondent;
  infrastructure: InfrastructureAssessment;
  serviceQuality: ServiceQuality;
  barriers: BarriersAssessment;
  additionalInfo: AdditionalInfo;
}

const STEPS = [
  'College Selection',
  'Respondent Info',
  'Infrastructure',
  'Service Quality',
  'Barriers',
  'Additional Info',
];

export function Questionnaire({ onSuccess, mode = 'comprehensive' }: { onSuccess?: () => void; mode?: 'comprehensive' | 'quick' | 'bulk' }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [saved, setSaved] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register, handleSubmit, watch, setValue, control, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      collegeId: '',
      respondent: {
        type: 'librarian',
        name: '',
        position: '',
        email: '',
      },
      infrastructure: {
        hardwareQuality: 3,
        softwareAvailability: 3,
        internetSpeed: 3,
        digitalCollection: 3,
        automationSystem: 'None',
      },
      serviceQuality: {
        overallSatisfaction: 5,
        serviceEfficiency: 5,
        staffHelpfulness: 5,
      },
      barriers: {
        financialBarrier: 3,
        technicalBarrier: 3,
        trainingBarrier: 3,
        policyBarrier: 3,
      },
      additionalInfo: {
        weeklyVisits: 0,
        ictTrainingReceived: false,
        remoteAccessAvailable: false,
        comments: '',
      },
    },
  });

  const watchedValues = watch();

  const progress = ((currentStep + 1) / STEPS.length) * 100;

  const saveToLocalStorage = () => {
    localStorage.setItem('questionnaire-draft', JSON.stringify(watchedValues));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const loadFromLocalStorage = () => {
    const saved = localStorage.getItem('questionnaire-draft');
    if (saved) {
      const data = JSON.parse(saved);
      Object.keys(data).forEach((key) => {
        setValue(key as any, data[key]);
      });
    }
  };

  const onSubmit = async (data: FormData) => {
    // Only submit if we're on the final step
    if (currentStep !== STEPS.length - 1) {
      return; // Don't submit if not on final step
    }

    if (isSubmitting) return; // Prevent double submission
    
    setIsSubmitting(true);
    try {
      console.log('Form submission started with data:', data);
      
      const college = COLLEGES.find((c) => c.id === data.collegeId);
      
      // Map form data to API format (keep camelCase since backend now supports it)
      const responseData = {
        college_id: data.collegeId,
        respondent: {
          type: data.respondent.type,
          name: data.respondent.name,
          position: data.respondent.position,
          email: data.respondent.email,
        },
        infrastructure: {
          hardwareQuality: data.infrastructure.hardwareQuality,
          softwareAvailability: data.infrastructure.softwareAvailability,
          internetSpeed: data.infrastructure.internetSpeed,
          digitalCollection: data.infrastructure.digitalCollection,
          automationSystem: data.infrastructure.automationSystem,
        },
        service_quality: {
          overallSatisfaction: data.serviceQuality.overallSatisfaction,
          serviceEfficiency: data.serviceQuality.serviceEfficiency,
          staffHelpfulness: data.serviceQuality.staffHelpfulness,
        },
        barriers: {
          financialBarrier: data.barriers.financialBarrier,
          technicalBarrier: data.barriers.technicalBarrier,
          trainingBarrier: data.barriers.trainingBarrier,
          policyBarrier: data.barriers.policyBarrier,
        },
        additional_info: {
          weeklyVisits: data.additionalInfo.weeklyVisits,
          ictTrainingReceived: data.additionalInfo.ictTrainingReceived,
          remoteAccessAvailable: data.additionalInfo.remoteAccessAvailable,
          comments: data.additionalInfo.comments,
          awarenessLevel: 3, // Default value
        },
      };

      console.log('Submitting response data:', responseData);

      // Submit to API
      const response = await apiClient.submitResponse(responseData);
      console.log('API response:', response);
      
      toast.success('Survey submitted successfully! Your submission is pending admin approval.');
      
      // Call onSuccess callback to trigger real-time updates
      if (onSuccess) {
        onSuccess();
      }
      
      // Clear local storage draft
      localStorage.removeItem('questionnaire-draft');
      
      // Reset form
      setCurrentStep(0);
      // Reset form values to defaults
      setValue('collegeId', '');
      setValue('respondent.name', '');
      setValue('respondent.position', '');
      setValue('respondent.email', '');
      setValue('respondent.type', 'librarian');
      
    } catch (error: any) {
      console.error('Submission error:', error);
      toast.error(error.message || 'Failed to submit survey. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = (e?: React.MouseEvent) => {
    e?.preventDefault(); // Prevent form submission
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = (e?: React.MouseEvent) => {
    e?.preventDefault(); // Prevent form submission
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="mx-auto max-w-4xl p-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Questionnaire</CardTitle>
            <Button variant="ghost" size="sm" onClick={saveToLocalStorage}>
              <Save className="mr-2 h-4 w-4" />
              Save Draft
            </Button>
          </div>
          {saved && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-2 flex items-center text-sm text-green-600"
            >
              <CheckCircle className="mr-2 h-4 w-4" />
              Draft saved successfully!
            </motion.div>
          )}
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="mb-2 flex justify-between text-sm text-gray-600">
              <span>Step {currentStep + 1} of {STEPS.length}</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
              <motion.div
                className="h-full bg-primary-600"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <AnimatePresence mode="wait">
              {currentStep === 0 && (
                <motion.div
                  key="step-0"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <h3 className="text-lg font-semibold">Select College</h3>
                  <Controller
                    name="collegeId"
                    control={control}
                    rules={{ required: 'Please select a college' }}
                    render={({ field }) => (
                      <Select
                        options={COLLEGES.map((c) => ({ value: c.id, label: c.name }))}
                        placeholder="Select a college"
                        value={field.value}
                        onChange={(value) => field.onChange(value)}
                      />
                    )}
                  />
                  {errors.collegeId && (
                    <p className="text-sm text-red-600">{errors.collegeId.message}</p>
                  )}
                </motion.div>
              )}

              {currentStep === 1 && (
                <motion.div
                  key="step-1"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <h3 className="text-lg font-semibold">Respondent Information</h3>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Respondent Type</label>
                    <Controller
                      name="respondent.type"
                      control={control}
                      rules={{ required: 'Please select respondent type' }}
                      render={({ field }) => (
                        <Select
                          options={[
                            { value: 'librarian', label: 'Librarian' },
                            { value: 'user', label: 'User' },
                          ]}
                          placeholder="Select respondent type"
                          value={field.value}
                          onChange={(value) => field.onChange(value)}
                        />
                      )}
                    />
                    {errors.respondent?.type && (
                      <p className="text-sm text-red-600">{errors.respondent.type.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Name</label>
                    <Input {...register('respondent.name', { required: 'Name is required' })} />
                    {errors.respondent?.name && (
                      <p className="text-sm text-red-600">{errors.respondent.name.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Position</label>
                    <Input {...register('respondent.position', { required: 'Position is required' })} />
                    {errors.respondent?.position && (
                      <p className="text-sm text-red-600">{errors.respondent.position.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Email (Optional)</label>
                    <Input type="email" {...register('respondent.email')} />
                  </div>
                </motion.div>
              )}

              {currentStep === 2 && (
                <motion.div
                  key="step-2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  <h3 className="text-lg font-semibold">Infrastructure Assessment</h3>
                  <div>
                    <Slider
                      label="Hardware Quality"
                      value={watchedValues.infrastructure?.hardwareQuality || 3}
                      onValueChange={(val) => setValue('infrastructure.hardwareQuality', val)}
                      min={1}
                      max={5}
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      {INFRASTRUCTURE_LABELS[watchedValues.infrastructure?.hardwareQuality as keyof typeof INFRASTRUCTURE_LABELS]}
                    </p>
                  </div>
                  <div>
                    <Slider
                      label="Software Availability"
                      value={watchedValues.infrastructure?.softwareAvailability || 3}
                      onValueChange={(val) => setValue('infrastructure.softwareAvailability', val)}
                      min={1}
                      max={5}
                    />
                  </div>
                  <div>
                    <Slider
                      label="Internet Speed"
                      value={watchedValues.infrastructure?.internetSpeed || 3}
                      onValueChange={(val) => setValue('infrastructure.internetSpeed', val)}
                      min={1}
                      max={5}
                    />
                  </div>
                  <div>
                    <Slider
                      label="Digital Collection"
                      value={watchedValues.infrastructure?.digitalCollection || 3}
                      onValueChange={(val) => setValue('infrastructure.digitalCollection', val)}
                      min={1}
                      max={5}
                    />
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Automation System</label>
                    <Controller
                      name="infrastructure.automationSystem"
                      control={control}
                      render={({ field }) => (
                        <Select
                          options={AUTOMATION_SYSTEMS.map((s) => ({ value: s, label: s }))}
                          placeholder="Select automation system"
                          value={field.value}
                          onChange={(value) => field.onChange(value)}
                        />
                      )}
                    />
                  </div>
                </motion.div>
              )}

              {currentStep === 3 && (
                <motion.div
                  key="step-3"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  <h3 className="text-lg font-semibold">Service Quality</h3>
                  <div>
                    <Slider
                      label="Overall Satisfaction"
                      value={watchedValues.serviceQuality?.overallSatisfaction || 5}
                      onValueChange={(val) => setValue('serviceQuality.overallSatisfaction', val)}
                      min={1}
                      max={10}
                    />
                  </div>
                  <div>
                    <Slider
                      label="Service Efficiency"
                      value={watchedValues.serviceQuality?.serviceEfficiency || 5}
                      onValueChange={(val) => setValue('serviceQuality.serviceEfficiency', val)}
                      min={1}
                      max={10}
                    />
                  </div>
                  <div>
                    <Slider
                      label="Staff Helpfulness"
                      value={watchedValues.serviceQuality?.staffHelpfulness || 5}
                      onValueChange={(val) => setValue('serviceQuality.staffHelpfulness', val)}
                      min={1}
                      max={10}
                    />
                  </div>
                </motion.div>
              )}

              {currentStep === 4 && (
                <motion.div
                  key="step-4"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  <h3 className="text-lg font-semibold">Barriers Assessment</h3>
                  <div>
                    <Slider
                      label="Financial Barrier"
                      value={watchedValues.barriers?.financialBarrier || 3}
                      onValueChange={(val) => setValue('barriers.financialBarrier', val)}
                      min={1}
                      max={5}
                    />
                  </div>
                  <div>
                    <Slider
                      label="Technical Barrier"
                      value={watchedValues.barriers?.technicalBarrier || 3}
                      onValueChange={(val) => setValue('barriers.technicalBarrier', val)}
                      min={1}
                      max={5}
                    />
                  </div>
                  <div>
                    <Slider
                      label="Training Barrier"
                      value={watchedValues.barriers?.trainingBarrier || 3}
                      onValueChange={(val) => setValue('barriers.trainingBarrier', val)}
                      min={1}
                      max={5}
                    />
                  </div>
                  <div>
                    <Slider
                      label="Policy Barrier"
                      value={watchedValues.barriers?.policyBarrier || 3}
                      onValueChange={(val) => setValue('barriers.policyBarrier', val)}
                      min={1}
                      max={5}
                    />
                  </div>
                </motion.div>
              )}

              {currentStep === 5 && (
                <motion.div
                  key="step-5"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <h3 className="text-lg font-semibold">Additional Information</h3>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Weekly Visits</label>
                    <Input
                      type="number"
                      {...register('additionalInfo.weeklyVisits', { valueAsNumber: true })}
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="ict-training"
                      {...register('additionalInfo.ictTrainingReceived')}
                    />
                    <label htmlFor="ict-training" className="text-sm font-medium">
                      ICT Training Received
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="remote-access"
                      {...register('additionalInfo.remoteAccessAvailable')}
                    />
                    <label htmlFor="remote-access" className="text-sm font-medium">
                      Remote Access Available
                    </label>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Comments</label>
                    <textarea
                      className="w-full rounded-md border border-gray-300 p-2"
                      rows={4}
                      {...register('additionalInfo.comments')}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="mt-8 flex justify-between">
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 0}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Previous
              </Button>
              {currentStep < STEPS.length - 1 ? (
                <Button 
                  type="button" 
                  onClick={nextStep}
                >
                  Next
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Submitting...' : 'Submit'}
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}