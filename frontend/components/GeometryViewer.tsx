'use client';

import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';
import type { SolidSpec } from '@/types';

interface GeometryViewerProps {
  solidSpec: SolidSpec;
  width?: number;
  height?: number;
}

function PyramidMesh({ params }: { params: Record<string, unknown> }) {
  const baseSide = (params.base_side as number) || 4;
  const height = (params.height as number) || 6;
  const baseShape = (params.base_shape as string) || 'square';

  const vertices: number[] = [];
  const indices: number[] = [];

  if (baseShape === 'square') {
    vertices.push(-baseSide / 2, 0, -baseSide / 2);
    vertices.push(baseSide / 2, 0, -baseSide / 2);
    vertices.push(baseSide / 2, 0, baseSide / 2);
    vertices.push(-baseSide / 2, 0, baseSide / 2);
    vertices.push(0, height, 0);

    indices.push(0, 1, 4, 1, 2, 4, 2, 3, 4, 3, 0, 4);
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();

  return (
    <group>
      <mesh geometry={geometry}>
        <meshStandardMaterial color="#88ccee" transparent opacity={0.7} side={THREE.DoubleSide} />
      </mesh>
      <lineSegments>
        <wireframeGeometry attach="geometry" args={[geometry]} />
        <lineBasicMaterial color="#0f172a" />
      </lineSegments>
    </group>
  );
}

function VertexLabel({ position, label }: { position: [number, number, number]; label: string }) {
  return (
    <Text position={position} fontSize={0.4} color="#0f172a" anchorX="center" anchorY="middle">
      {label}
    </Text>
  );
}

export default function GeometryViewer({ solidSpec, width, height = 320 }: GeometryViewerProps) {
  const { solid_type, params } = solidSpec;
  const [showMeasurements, setShowMeasurements] = useState(Boolean(params.show_measurements));

  if (solid_type !== 'pyramid') {
    return (
      <div className="flex h-full items-center justify-center rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-500">
        Geometry type not yet supported: {solid_type}
      </div>
    );
  }

  const apexLabel = (params.apex_label as string) || 'S';
  const baseLabels = (params.base_labels as string[]) || ['A', 'B', 'C', 'D'];
  const baseSide = (params.base_side as number) || 4;
  const pyramidHeight = (params.height as number) || 6;

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">3D hinh chop</div>
          <div className="text-xs text-slate-500">Xoay, phong to, va bat tat thong so hinh hoc.</div>
        </div>
        <button
          type="button"
          onClick={() => setShowMeasurements((value) => !value)}
          className="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
        >
          {showMeasurements ? 'An so do' : 'Hien so do'}
        </button>
      </div>

      <div style={{ width: width ?? '100%', height }} className="bg-slate-50">
        <Canvas camera={{ position: [8, 8, 8], fov: 50 }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[5, 10, 5]} intensity={0.8} />
          <PyramidMesh params={params} />
          <VertexLabel position={[0, pyramidHeight, 0]} label={apexLabel} />
          <VertexLabel position={[-baseSide / 2, 0, -baseSide / 2]} label={baseLabels[0]} />
          <VertexLabel position={[baseSide / 2, 0, -baseSide / 2]} label={baseLabels[1]} />
          <VertexLabel position={[baseSide / 2, 0, baseSide / 2]} label={baseLabels[2]} />
          <VertexLabel position={[-baseSide / 2, 0, baseSide / 2]} label={baseLabels[3]} />
          {(params.show_altitude as boolean) && (
            <lineSegments>
              <bufferGeometry>
                <float32BufferAttribute attach="attributes-position" args={[[0, pyramidHeight, 0, 0, 0, 0], 3]} count={2} itemSize={3} />
              </bufferGeometry>
              <lineDashedMaterial color="red" dashSize={0.2} gapSize={0.1} />
            </lineSegments>
          )}
          <OrbitControls enablePan={false} />
          <gridHelper args={[10, 10]} />
        </Canvas>
      </div>

      {showMeasurements && (
        <div className="grid gap-2 border-t border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 sm:grid-cols-2">
          <div>Canh day: {baseSide}</div>
          <div>Chieu cao: {pyramidHeight}</div>
        </div>
      )}
    </div>
  );
}
