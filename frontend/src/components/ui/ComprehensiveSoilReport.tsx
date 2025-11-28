import React, { useEffect, useState } from 'react';
import {
  Sprout,
  ThumbsUp,
  ThumbsDown,
  Star,
  Wheat,
  Calendar,
  FlaskConical,
  Clock,
  Target,
  Download,
  Share2,
  CheckCircle2,
  AlertTriangle,
  Leaf,
} from 'lucide-react';

interface SoilAnalysis {
  assessment: string;
  pros: string[];
  cons: string[];
  rating: string;
}

interface CropRecommendation {
  crop: string;
  reason: string;
  season: string;
}

interface FertilizerRecommendation {
  fertilizer: string;
  type: string;
  application: string;
  timing: string;
  purpose: string;
}

interface ComprehensiveReportData {
  soilAnalysis: SoilAnalysis;
  cropRecommendations: CropRecommendation[];
  fertilizerRecommendations: FertilizerRecommendation[];
}

interface ComprehensiveSoilReportProps {
  report: {
    english: ComprehensiveReportData;
    hindi: ComprehensiveReportData;
    metadata?: any;
  };
  sessionId: string;
  onClose?: () => void;
}

export const ComprehensiveSoilReport: React.FC<ComprehensiveSoilReportProps> = ({
  report,
  sessionId,
  onClose,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [language, setLanguage] = useState<'english' | 'hindi'>('english');

  useEffect(() => {
    setTimeout(() => setIsVisible(true), 100);
  }, []);

  // Get current language report
  const currentReport = report[language];

  const getRatingColor = (rating: string) => {
    switch (rating.toLowerCase()) {
      case 'excellent':
        return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'good':
        return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
      case 'fair':
        return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      default:
        return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  const getRatingScore = (rating: string) => {
    switch (rating.toLowerCase()) {
      case 'excellent':
        return 95;
      case 'good':
        return 75;
      case 'fair':
        return 55;
      default:
        return 40;
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(
        `http://localhost:8001/api/reports/download/${sessionId}/pdf?language=${language}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to download PDF');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `soil_report_${sessionId}_${language}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF. Please try again.');
    }
  };

  const handleShare = () => {
    console.log('Share report');
    // TODO: Implement share functionality
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'english' ? 'hindi' : 'english');
  };

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
                  Comprehensive Soil Health Report
                </h2>
                <p className="text-green-100 text-sm">
                  Detailed analysis with crop & fertilizer recommendations
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={toggleLanguage}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors font-semibold text-white text-sm"
                title="Toggle Language"
              >
                {language === 'english' ? 'हिंदी' : 'English'}
              </button>
              <button
                onClick={handleDownload}
                className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                title="Download PDF"
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
          {/* Soil Analysis Section */}
          <div className="space-y-4">
            {/* Rating Badge */}
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                <FlaskConical className="w-6 h-6 text-green-400" />
                Soil Analysis
              </h3>
              <div
                className={`px-4 py-2 rounded-full border flex items-center gap-2 ${getRatingColor(
                  currentReport.soilAnalysis.rating
                )}`}
              >
                <Star className="w-5 h-5 fill-current" />
                <span className="font-bold">{currentReport.soilAnalysis.rating}</span>
              </div>
            </div>

            {/* Health Score Bar */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-gray-300">Soil Health Score</span>
                <span className="text-2xl font-bold text-green-400">
                  {getRatingScore(currentReport.soilAnalysis.rating)}/100
                </span>
              </div>
              <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-1000 ease-out"
                  style={{ width: `${getRatingScore(currentReport.soilAnalysis.rating)}%` }}
                />
              </div>
            </div>

            {/* Assessment */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <p className="text-gray-300 leading-relaxed">{currentReport.soilAnalysis.assessment}</p>
            </div>

            {/* Pros and Cons */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Pros */}
              <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <ThumbsUp className="w-5 h-5 text-green-400" />
                  Strengths
                </h4>
                <ul className="space-y-2">
                  {currentReport.soilAnalysis.pros.map((pro, index) => (
                    <li key={index} className="flex gap-3 text-gray-300 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Cons */}
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <ThumbsDown className="w-5 h-5 text-yellow-400" />
                  Areas to Watch
                </h4>
                <ul className="space-y-2">
                  {currentReport.soilAnalysis.cons.map((con, index) => (
                    <li key={index} className="flex gap-3 text-gray-300 text-sm">
                      <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                      <span>{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Crop Recommendations */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-white flex items-center gap-2">
              <Wheat className="w-6 h-6 text-green-400" />
              Recommended Crops
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {currentReport.cropRecommendations.map((crop, index) => (
                <div
                  key={index}
                  className="bg-gray-800/50 border border-gray-700 rounded-xl p-5 hover:border-green-500/50 transition-all duration-300 animate-fade-in"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="text-lg font-bold text-white">{crop.crop}</h4>
                    <Leaf className="w-5 h-5 text-green-400 flex-shrink-0" />
                  </div>
                  <p className="text-gray-300 text-sm mb-3">{crop.reason}</p>
                  <div className="flex items-center gap-2 text-xs text-gray-400 bg-gray-700/50 rounded-lg px-3 py-2">
                    <Calendar className="w-4 h-4" />
                    <span>{crop.season}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Fertilizer Recommendations */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-white flex items-center gap-2">
              <FlaskConical className="w-6 h-6 text-green-400" />
              Fertilizer Recommendations
            </h3>
            <div className="space-y-4">
              {currentReport.fertilizerRecommendations.map((fertilizer, index) => (
                <div
                  key={index}
                  className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 hover:border-green-500/30 transition-all duration-300 animate-fade-in"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="text-lg font-bold text-white mb-1">
                        {fertilizer.fertilizer}
                      </h4>
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                          fertilizer.type.toLowerCase() === 'organic'
                            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                            : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                        }`}
                      >
                        {fertilizer.type}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex gap-3">
                      <Target className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-semibold text-gray-300 mb-1">Application</p>
                        <p className="text-sm text-gray-400">{fertilizer.application}</p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <Clock className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-semibold text-gray-300 mb-1">Timing</p>
                        <p className="text-sm text-gray-400">{fertilizer.timing}</p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-semibold text-gray-300 mb-1">Purpose</p>
                        <p className="text-sm text-gray-400">{fertilizer.purpose}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
