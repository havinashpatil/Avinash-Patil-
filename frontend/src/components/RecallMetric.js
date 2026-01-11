/**
 * Recall Metric Display Component
 * Shows model sensitivity with visual gauge and explanation
 */
import React from 'react';
import { FaInfoCircle } from 'react-icons/fa';

const RecallMetric = ({ metrics }) => {
    const overallRecall = metrics?.recall || 0;
    const perClassMetrics = metrics?.per_class_metrics || {};

    const getRecallColor = (recall) => {
        if (recall >= 0.95) return 'success';
        if (recall >= 0.85) return 'warning';
        return 'danger';
    };

    const recallPercentage = Math.round(overallRecall * 100);
    const recallColor = getRecallColor(overallRecall);

    return (
        <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-800">
                    Model Sensitivity (Recall)
                </h3>
                <div className="group relative">
                    <FaInfoCircle className="text-primary-500 cursor-help" />
                    <div className="absolute right-0 bottom-full mb-2 w-64 p-3 bg-neutral-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                        <p className="font-medium mb-1">What is Recall?</p>
                        <p className="text-xs text-neutral-300">
                            Recall measures the model's ability to detect cancer cells. Higher recall means fewer false negatives (missed detections).
                        </p>
                    </div>
                </div>
            </div>

            {/* Overall Recall Gauge */}
            <div className="mb-6">
                <div className="flex items-end justify-between mb-2">
                    <span className="text-sm font-medium text-neutral-600">Overall Recall</span>
                    <span className={`text-3xl font-bold text-${recallColor}-600`}>
                        {recallPercentage}%
                    </span>
                </div>

                {/* Progress Bar */}
                <div className="w-full h-4 bg-neutral-200 rounded-full overflow-hidden">
                    <div
                        className={`h-full bg-gradient-to-r from-${recallColor}-500 to-${recallColor}-600 transition-all duration-1000`}
                        style={{ width: `${recallPercentage}%` }}
                    ></div>
                </div>

                {/* Trust Indicator */}
                <div className="mt-3">
                    {recallPercentage >= 95 ? (
                        <div className="badge-success">
                            ✓ High Sensitivity - Minimal False Negatives
                        </div>
                    ) : recallPercentage >= 85 ? (
                        <div className="badge-warning">
                            ⚠ Moderate Sensitivity
                        </div>
                    ) : (
                        <div className="badge-danger">
                            ⚠ Low Sensitivity - Review Required
                        </div>
                    )}
                </div>
            </div>

            {/* Per-Class Breakdown */}
            {Object.keys(perClassMetrics).length > 0 && (
                <div>
                    <h4 className="text-sm font-semibold text-neutral-700 mb-3">
                        Per-Class Sensitivity
                    </h4>
                    <div className="space-y-3">
                        {Object.entries(perClassMetrics).map(([className, metrics]) => {
                            const classRecall = metrics.recall || 0;
                            const classRecallPct = Math.round(classRecall * 100);
                            const colorClass = getRecallColor(classRecall);

                            return (
                                <div key={className} className="space-y-1">
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-neutral-700 font-medium">
                                            {className}
                                        </span>
                                        <span className={`text-sm font-semibold text-${colorClass}-600`}>
                                            {classRecallPct}%
                                        </span>
                                    </div>
                                    <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full bg-${colorClass}-500`}
                                            style={{ width: `${classRecallPct}%` }}
                                        ></div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default RecallMetric;
