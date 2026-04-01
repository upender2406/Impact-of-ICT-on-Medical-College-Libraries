import React from 'react';
import { cn } from '@/lib/utils';

interface SliderProps {
  label?: string;
  value: number;
  onValueChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  className?: string;
}

export function Slider({ 
  label, 
  value, 
  onValueChange, 
  min, 
  max, 
  step = 1, 
  className 
}: SliderProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <div className="flex justify-between">
          <label className="text-sm font-medium">{label}</label>
          <span className="text-sm text-gray-500">{value}</span>
        </div>
      )}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onValueChange(Number(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
      />
      <div className="flex justify-between text-xs text-gray-500">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}