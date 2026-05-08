'use client';

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import type { MasteryData } from '@/types';

interface MasteryRadarProps {
  data: MasteryData;
}

export default function MasteryRadar({ data }: MasteryRadarProps) {
  const chartData = Object.entries(data.mastery_by_topic).map(([topic, score]) => ({
    topic: topic.split('.').pop(),
    score: score * 100,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={chartData}>
        <PolarGrid />
        <PolarAngleAxis dataKey="topic" />
        <Radar name="Thành thạo" dataKey="score" stroke="#2563eb" fill="#2563eb" fillOpacity={0.3} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
