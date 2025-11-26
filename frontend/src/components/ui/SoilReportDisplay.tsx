import React, { useEffect, useState } from 'react';
import {
  Sprout,
  Droplets,
  Wind,
  FlaskConical,
  MapPin,
  Leaf,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Download,
  Share2,
} from 'lucide-react';

interface ReportSection {
  title: string;
  content: string[];
}

interface SoilReportData {
  type?: string;
  content?: string;
  sections?: ReportSection[];
  // Structured report fields
  soilHealth?: {
    score: number;
    status: string;
    description: string;
  };
  analysis?: {
    soilColor?: string;
    moistureLevel?: string;
    phLevel?: string;
    soilType?: string;
    earthworms?: string;
  };
  recommendations?: {
    fertilizers?: string[];
    practices?: string[];
    warnings?: string[];
  };
  nextSteps?: string[];
}

interface SoilReportDisplayProps {
  report: SoilReportData;
  onClose?: () => void;
}

export const SoilReportDisplay: React.FC<SoilReportDisplayProps> = ({
  report,
  onClose,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation
    setTimeout(() => setIsVisible(true), 100);
  }, []);

  const handleDownload = () => {
    // TODO: Implement PDF download
    console.log('Download report');
  };

  const handleShare = () => {
    // TODO: Implement share functionality
    console.log('Share report');
  };

  // Render structured report
  if (report.soilHealth || report.analysis) {
    return (
      <div
        className={`transition-all duration-700 transform ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        }`}
      >
        <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl shadow-2xl border border-gray-700 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <Sprout className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    Your Soil Health Report
                  </h2>
                  <p className="text-green-100 text-sm">
                    Personalized analysis and recommendations
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleDownload}
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                  title="Download Report"
                >
                  <Download className="w-5 h-5 text-white" />
                </button>
                <button
                  onClick={handleShare}
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                  title="Share Report"
                >
                  <Share2 className="w-5 h-5 text-white" />
                </button>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Soil Health Score */}
            {report.soilHealth && (
              <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-xl p-6 animate-fade-in">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-400" />
                    Soil Health Score
                  </h3>
                  <div className="text-4xl font-bold text-green-400">
                    {report.soilHealth.score}/100
                  </div>
                </div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden mb-3">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-1000 ease-out"
                    style={{ width: `${report.soilHealth.score}%` }}
                  />
                </div>
                <p className="text-gray-300">{report.soilHealth.description}</p>
              </div>
            )}

            {/* Analysis Section */}
            {report.analysis && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {report.analysis.soilColor && (
                  <AnalysisCard
                    icon={Sprout}
                    label="Soil Color"
                    value={report.analysis.soilColor}
                    delay={100}
                  />
                )}
                {report.analysis.moistureLevel && (
                  <AnalysisCard
                    icon={Droplets}
                    label="Moisture Level"
                    value={report.analysis.moistureLevel}
                    delay={200}
                  />
                )}
                {report.analysis.phLevel && (
                  <AnalysisCard
                    icon={FlaskConical}
                    label="pH Level"
                    value={report.analysis.phLevel}
                    delay={300}
                  />
                )}
                {report.analysis.soilType && (
                  <AnalysisCard
                    icon={Leaf}
                    label="Soil Type"
                    value={report.analysis.soilType}
                    delay={400}
                  />
                )}
              </div>
            )}

            {/* Recommendations */}
            {report.recommendations && (
              <div className="space-y-4">
                {report.recommendations.fertilizers && report.recommendations.fertilizers.length > 0 && (
                  <RecommendationSection
                    title="Recommended Fertilizers"
                    icon={Leaf}
                    items={report.recommendations.fertilizers}
                    type="success"
                  />
                )}
                {report.recommendations.practices && report.recommendations.practices.length > 0 && (
                  <RecommendationSection
                    title="Best Practices"
                    icon={CheckCircle2}
                    items={report.recommendations.practices}
                    type="info"
                  />
                )}
                {report.recommendations.warnings && report.recommendations.warnings.length > 0 && (
                  <RecommendationSection
                    title="Important Warnings"
                    icon={AlertCircle}
                    items={report.recommendations.warnings}
                    type="warning"
                  />
                )}
              </div>
            )}

            {/* Next Steps */}
            {report.nextSteps && report.nextSteps.length > 0 && (
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-400" />
                  Next Steps
                </h3>
                <ol className="space-y-2">
                  {report.nextSteps.map((step, index) => (
                    <li key={index} className="flex gap-3 text-gray-300">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center text-blue-400 text-sm font-semibold">
                        {index + 1}
                      </span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Render text-based report
  return (
    <div
      className={`transition-all duration-700 transform ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      }`}
    >
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl shadow-2xl border border-gray-700 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                <Sprout className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">
                  Your Soil Health Report
                </h2>
                <p className="text-green-100 text-sm">
                  Personalized analysis and recommendations
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleDownload}
                className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                title="Download Report"
              >
                <Download className="w-5 h-5 text-white" />
              </button>
              <button
                onClick={handleShare}
                className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                title="Share Report"
              >
                <Share2 className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {report.sections && report.sections.length > 0 ? (
            report.sections.map((section, index) => (
              <div
                key={index}
                className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 animate-fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <h3 className="text-lg font-semibold text-white mb-3">
                  {section.title}
                </h3>
                <div className="space-y-2">
                  {section.content.map((line, lineIndex) => (
                    <p key={lineIndex} className="text-gray-300">
                      {line}
                    </p>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <p className="text-gray-300 whitespace-pre-wrap">{report.content}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Helper Components
interface AnalysisCardProps {
  icon: React.ElementType;
  label: string;
  value: string;
  delay: number;
}

const AnalysisCard: React.FC<AnalysisCardProps> = ({ icon: Icon, label, value, delay }) => (
  <div
    className="bg-gray-800/50 border border-gray-700 rounded-xl p-4 animate-fade-in"
    style={{ animationDelay: `${delay}ms` }}
  >
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
        <Icon className="w-5 h-5 text-green-400" />
      </div>
      <div>
        <p className="text-sm text-gray-400">{label}</p>
        <p className="text-lg font-semibold text-white">{value}</p>
      </div>
    </div>
  </div>
);

interface RecommendationSectionProps {
  title: string;
  icon: React.ElementType;
  items: string[];
  type: 'success' | 'info' | 'warning';
}

const RecommendationSection: React.FC<RecommendationSectionProps> = ({
  title,
  icon: Icon,
  items,
  type,
}) => {
  const colors = {
    success: {
      bg: 'bg-green-500/10',
      border: 'border-green-500/30',
      icon: 'text-green-400',
      text: 'text-gray-300',
    },
    info: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      icon: 'text-blue-400',
      text: 'text-gray-300',
    },
    warning: {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
      icon: 'text-yellow-400',
      text: 'text-gray-300',
    },
  };

  const style = colors[type];

  return (
    <div className={`${style.bg} border ${style.border} rounded-xl p-6 animate-fade-in`}>
      <h3 className={`text-lg font-semibold text-white mb-4 flex items-center gap-2`}>
        <Icon className={`w-5 h-5 ${style.icon}`} />
        {title}
      </h3>
      <ul className="space-y-2">
        {items.map((item, index) => (
          <li key={index} className={`flex gap-3 ${style.text}`}>
            <span className="flex-shrink-0 mt-1.5 w-1.5 h-1.5 bg-current rounded-full" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
