// src/components/SummaryPage.tsx
import React from "react";
import { SoilTestResult, Language } from "../api/client";
import jsPDF from "jspdf";

interface SummaryPageProps {
  answers: SoilTestResult;
  language: Language;
  isComplete: boolean;
}

const FIELD_LABELS: Record<string, Record<Language, string>> = {
  color: { en: "Color", hi: "रंग" },
  moisture: { en: "Moisture", hi: "नमी" },
  smell: { en: "Smell", hi: "गंध" },
  ph_category: { en: "pH Category", hi: "pH श्रेणी" },
  ph_value: { en: "pH Value", hi: "pH मान" },
  soil_type: { en: "Soil Type", hi: "मिट्टी का प्रकार" },
  earthworms: { en: "Earthworms", hi: "केंचुए" },
  location: { en: "Location", hi: "स्थान" },
  fertilizer_used: { en: "Fertilizer Used", hi: "उपयोग की गई खाद" },
};

export default function SummaryPage({ answers, language, isComplete }: SummaryPageProps) {
  const fields = Object.keys(FIELD_LABELS);

  const downloadPdf = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text("Agrovers Soil Report", 14, 20);
    doc.setFontSize(11);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28);

    let y = 40;
    fields.forEach((f) => {
      const label = FIELD_LABELS[f]?.[language] || f;
      const value = (answers as any)[f] ?? "—";
      doc.setFontSize(12);
      doc.text(`${label}: ${String(value)}`, 14, y);
      y += 8;
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
    });

    doc.save("agrovers-soil-report.pdf");
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold text-center mb-6">{language === "hi" ? "सारांश" : "Summary"}</h2>
        {isComplete && (
          <div className="mb-6 p-4 bg-green-100 border-l-4 border-green-500 rounded">
            <p className="text-green-800 font-semibold">
              {language === "hi" ? "✅ डेटा सफलतापूर्वक संकलित किया गया।" : "✅ Data collected successfully."}
            </p>
          </div>
        )}

        <div className="space-y-3">
          {fields.map((field) => {
            const val = (answers as any)[field];
            if (val === undefined || val === null) return null;
            const label = FIELD_LABELS[field]?.[language] || field;
            return (
              <div key={field} className="flex justify-between items-center py-2 border-b">
                <span className="text-gray-700 font-medium">{label}</span>
                <span className="text-gray-900">{String(val)}</span>
              </div>
            );
          })}
        </div>

        <div className="mt-6 flex gap-3 justify-center">
          <button onClick={downloadPdf} className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-semibold">
            {language === "hi" ? "PDF डाउनलोड करें" : "Download PDF"}
          </button>
        </div>
      </div>
    </div>
  );
}
