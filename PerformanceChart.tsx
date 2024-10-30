'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const performanceData = [
  { name: 'Jan', accuracy: 94, latency: 120 },
  { name: 'Feb', accuracy: 95, latency: 115 },
  { name: 'Mar', accuracy: 94, latency: 130 },
  { name: 'Apr', accuracy: 96, latency: 110 },
  { name: 'May', accuracy: 95, latency: 105 },
  { name: 'Jun', accuracy: 97, latency: 100 },
];

const PerformanceChart = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Model Performance</CardTitle>
        <CardDescription>Accuracy and latency over time</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={performanceData}>
              <XAxis dataKey="name" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="accuracy" 
                stroke="#2563eb" 
                strokeWidth={2} 
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="latency" 
                stroke="#16a34a" 
                strokeWidth={2} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

export default PerformanceChart;