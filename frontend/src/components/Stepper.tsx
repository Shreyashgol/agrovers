// src/components/Stepper.tsx
import React from "react";
import { Language } from "../api/client";

interface StepperProps {
  currentStep: number;
  totalSteps: number;
  currentParameter: string;
  language: Language;
  allParameters: string[];   // REQUIRED
  completedSteps: number;    // REQUIRED
}

const PARAMETER_NAMES: Record<string, Record<Language, string>> = {
  color: { en: "Color", hi: "रंग" },
  moisture: { en: "Moisture", hi: "नमी" },
  smell: { en: "Smell", hi: "गंध" },
  ph: { en: "pH", hi: "pH" },
  soil_type: { en: "Soil Type", hi: "मिट्टी का प्रकार" },
  earthworms: { en: "Earthworms", hi: "केंचुए" },
  location: { en: "Location", hi: "स्थान" },
  fertilizer_used: { en: "Fertilizer", hi: "खाद" },
};

export default function Stepper({
  currentStep,
  totalSteps,
  currentParameter,
  language,
  allParameters,
  completedSteps,
}: StepperProps) {
  
  const percent = Math.round((currentStep / Math.max(totalSteps, 1)) * 100);

  return (
    <div className="md:flex gap-6">
      {/* LEFT SIDEBAR */}
      <aside className="hidden md:block w-56 bg-white/5 rounded-xl p-4 border border-white/10">
        <h4 className="text-sm text-emerald-200 font-semibold mb-3">
          {language === "hi" ? "प्रश्न सूची" : "Questions"}
        </h4>

        <ul className="space-y-2">
          {allParameters.map((p, idx) => {
            const name = PARAMETER_NAMES[p]?.[language] || p;
            const stepNo = idx + 1;
            const done = stepNo <= completedSteps;
            const isActive = stepNo === currentStep;

            return (
              <li key={p} className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold 
                    ${done ? "bg-emerald-500 text-white" :
                      isActive ? "bg-emerald-600 text-white" :
                      "bg-white/10 text-emerald-200"}`}
                >
                  {done ? "✓" : stepNo}
                </div>

                <span className={`${isActive ? "text-white" : "text-neutral-300"} text-sm`}>
                  {name}
                </span>
              </li>
            );
          })}
        </ul>
      </aside>

      {/* TOP BAR */}
      <div className="flex-1">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-neutral-300">
              {language === "hi" ? "चरण" : "Step"} {currentStep}
              {" "}
              {language === "hi" ? "का" : "of"}
              {" "}
              {totalSteps}
            </span>

            <span className="text-sm text-emerald-300 font-semibold">
              {PARAMETER_NAMES[currentParameter]?.[language] || currentParameter}
            </span>
          </div>

          {/* PROGRESS BAR */}
          <div className="w-full bg-white/10 rounded-full h-2">
            <div
              className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
