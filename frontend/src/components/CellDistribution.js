/**
 * Cell Distribution Visualization Component
 * Shows predicted probabilities with Chart.js
 */
import React from 'react';
import { Pie } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const CellDistribution = ({ probabilities }) => {
    if (!probabilities || Object.keys(probabilities).length === 0) {
        return (
            <div className="glass-card p-6">
                <p className="text-neutral-600 text-center">No distribution data available</p>
            </div>
        );
    }

    // Prepare data for chart
    const labels = Object.keys(probabilities);
    const dataValues = labels.map(label => probabilities[label] * 100);

    // Color palette - malignant cells in red tones, normal in blue/green tones
    const getColor = (label) => {
        const lowerLabel = label.toLowerCase();
        if (lowerLabel.includes('blast') || lowerLabel.includes('malignant') || lowerLabel.includes('cancer')) {
            return {
                bg: 'rgba(230, 0, 0, 0.8)',
                border: 'rgba(230, 0, 0, 1)'
            };
        } else {
            const colors = [
                { bg: 'rgba(46, 143, 255, 0.8)', border: 'rgba(46, 143, 255, 1)' },
                { bg: 'rgba(0, 184, 148, 0.8)', border: 'rgba(0, 184, 148, 1)' },
                { bg: 'rgba(255, 198, 0, 0.8)', border: 'rgba(255, 198, 0, 1)' },
                { bg: 'rgba(108, 92, 231, 0.8)', border: 'rgba(108, 92, 231, 1)' },
            ];
            const index = labels.indexOf(label) % colors.length;
            return colors[index];
        }
    };

    const backgroundColors = labels.map(label => getColor(label).bg);
    const borderColors = labels.map(label => getColor(label).border);

    const data = {
        labels,
        datasets: [
            {
                data: dataValues,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2,
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 15,
                    font: {
                        size: 12,
                        family: 'Inter'
                    },
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            tooltip: {
                callbacks: {
                    label: (context) => {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        return `${label}: ${value.toFixed(2)}%`;
                    }
                },
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: {
                    size: 14
                },
                bodyFont: {
                    size: 13
                }
            }
        }
    };

    // Sort probabilities for list view
    const sortedProbs = Object.entries(probabilities)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value);

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-neutral-800 mb-6">
                Cell Type Distribution
            </h3>

            {/* Chart */}
            <div className="h-64 mb-6">
                <Pie data={data} options={options} />
            </div>

            {/* List View */}
            <div className="space-y-3">
                {sortedProbs.map(({ name, value }) => {
                    const percentage = (value * 100).toFixed(2);
                    const isMalignant = name.toLowerCase().includes('blast') ||
                        name.toLowerCase().includes('malignant') ||
                        name.toLowerCase().includes('cancer');

                    return (
                        <div key={name} className={`p-3 rounded-lg ${isMalignant ? 'bg-danger-50 border-l-4 border-danger-500' : 'bg-neutral-50'}`}>
                            <div className="flex items-center justify-between">
                                <span className={`font-medium ${isMalignant ? 'text-danger-700' : 'text-neutral-700'}`}>
                                    {name}
                                    {isMalignant && <span className="ml-2 text-xs">⚠️ Malignant</span>}
                                </span>
                                <span className={`text-lg font-bold ${isMalignant ? 'text-danger-600' : 'text-primary-600'}`}>
                                    {percentage}%
                                </span>
                            </div>
                            <div className="w-full h-2 bg-neutral-200 rounded-full mt-2 overflow-hidden">
                                <div
                                    className={`h-full ${isMalignant ? 'bg-danger-500' : 'bg-primary-500'}`}
                                    style={{ width: `${percentage}%` }}
                                ></div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default CellDistribution;
