'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';

interface GeometryViewerProps {
  solidSpec: { solid_type: string; params: Record<string, unknown>; highlights?: string[]; animated?: boolean };
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
        <meshStandardMaterial color="#88ccee" transparent opacity={0.6} side={THREE.DoubleSide} />
      </mesh>
      <lineSegments>
        <wireframeGeometry attach="geometry" args={[geometry]} />
        <lineBasicMaterial color="#444" />
      </lineSegments>
    </group>
  );
}

function VertexLabel({ position, label }: { position: [number, number, number]; label: string }) {
  return (
    <Text position={position} fontSize={0.4} color="#000" anchorX="center" anchorY="middle">
      {label}
    </Text>
  );
}

export default function GeometryViewer({ solidSpec, width = 400, height = 300 }: GeometryViewerProps) {
  const { solid_type, params, highlights } = solidSpec;

  if (solid_type !== 'pyramid') {
    return <div className="flex items-center justify-center h-full text-gray-500">Geometry type not yet supported: {solid_type}</div>;
  }

  const apexLabel = (params.apex_label as string) || 'S';
  const baseLabels = (params.base_labels as string[]) || ['A', 'B', 'C', 'D'];
  const baseSide = (params.base_side as number) || 4;
  const pyramidHeight = (params.height as number) || 6;

  return (
    <div style={{ width, height }} className="border rounded bg-gray-50">
      <Canvas camera={{ position: [8, 8, 8], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 10, 5]} intensity={0.8} />
        <PyramidMesh params={params} />
        <VertexLabel position={[0, pyramidHeight, 0]} label={apexLabel} />
        <VertexLabel position={[-baseSide / 2, 0, -baseSide / 2]} label={baseLabels[0]} />
        <VertexLabel position={[baseSide / 2, 0, -baseSide / 2]} label={baseLabels[1]} />
        <VertexLabel position={[baseSide / 2, 0, baseSide / 2]} label={baseLabels[2]} />
        <VertexLabel position={[-baseSide / 2, 0, baseSide / 2]} label={baseLabels[3]} />
        {params.show_altitude && (
          <lineSegments>
            <bufferGeometry>
              <float32BufferAttribute attach="attributes-position" args={[[0, pyramidHeight, 0, 0, 0, 0]]} count={2} itemSize={3} />
            </bufferGeometry>
            <lineDashedMaterial color="red" dashSize={0.2} gapSize={0.1} />
          </lineSegments>
        )}
        <OrbitControls />
        <gridHelper args={[10, 10]} />
      </Canvas>
    </div>
  );
}
