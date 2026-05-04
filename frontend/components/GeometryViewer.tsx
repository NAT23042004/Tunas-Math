"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

interface GeometryViewerProps {
  solid_type?: string;
  params?: {
    base_shape?: string;
    base_side?: number;
    height?: number;
    radius?: number;
    [key: string]: any;
  };
}

export function GeometryViewer({ solid_type = "pyramid", params }: GeometryViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const frameRef = useRef<number>(0);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf7f4ee);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      50,
      canvasRef.current.clientWidth / canvasRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(8, 6, 8);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current,
      antialias: true,
    });
    renderer.setSize(canvasRef.current.clientWidth, canvasRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    rendererRef.current = renderer;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Create geometry based on type
    if (solid_type === "pyramid" && params) {
      createPyramid(scene, params);
    } else {
      // Default: create a simple pyramid
      createPyramid(scene, { base_side: 4, height: 6 });
    }

    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(20, 20);
    const groundMaterial = new THREE.MeshLambertMaterial({ color: 0xe8e3d8 });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Animation loop
    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);

      // Slow rotation
      if (scene.children.length > 0) {
        const geometry = scene.children.find((child) => child.userData.isGeometry);
        if (geometry) {
          geometry.rotation.y += 0.005;
        }
      }

      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      if (!canvasRef.current) return;
      const width = canvasRef.current.clientWidth;
      const height = canvasRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(frameRef.current);
      renderer.dispose();
    };
  }, [solid_type, params]);

  return (
    <div className="w-full h-full flex items-center justify-center">
      <canvas ref={canvasRef} className="w-full h-full cursor-grab active:cursor-grabbing" />
    </div>
  );
}

function createPyramid(scene: THREE.Scene, params: any) {
  const baseSide = params.base_side || 4;
  const height = params.height || 6;

  // Create pyramid geometry
  const shape = new THREE.Shape();
  const halfBase = baseSide / 2;

  // Square base
  shape.moveTo(-halfBase, -halfBase);
  shape.lineTo(halfBase, -halfBase);
  shape.lineTo(halfBase, halfBase);
  shape.lineTo(-halfBase, halfBase);
  shape.lineTo(-halfBase, -halfBase);

  // Extrude to create base
  const extrudeSettings = {
    depth: 0.1,
    bevelEnabled: false,
  };
  const baseGeometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
  const baseMaterial = new THREE.MeshLambertMaterial({
    color: 0xcccccc,
    transparent: true,
    opacity: 0.3,
  });
  const base = new THREE.Mesh(baseGeometry, baseMaterial);
  base.rotation.x = -Math.PI / 2;
  base.receiveShadow = true;
  scene.add(base);

  // Create pyramid vertices
  const vertices = new Float32Array([
    // Base
    -halfBase, 0, -halfBase,  // 0
    halfBase, 0, -halfBase,   // 1
    halfBase, 0, halfBase,    // 2
    -halfBase, 0, halfBase,   // 3
    // Apex
    0, height, 0,              // 4
  ]);

  const indices = [
    0, 1, 4,  // Front face
    1, 2, 4,  // Right face
    2, 3, 4,  // Back face
    3, 0, 4,  // Left face
  ];

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
  geometry.setIndex(indices);

  const material = new THREE.MeshLambertMaterial({
    color: 0xc2391e,
    transparent: true,
    opacity: 0.6,
    side: THREE.DoubleSide,
  });

  const pyramid = new THREE.Mesh(geometry, material);
  pyramid.castShadow = true;
  pyramid.userData = { isGeometry: true };
  scene.add(pyramid);

  // Add wireframe
  const wireframe = new THREE.LineSegments(
    new THREE.WireframeGeometry(geometry),
    new THREE.LineBasicMaterial({ color: 0xc2391e, linewidth: 2 })
  );
  pyramid.add(wireframe);

  // Add labels
  addLabel(scene, "S", new THREE.Vector3(0, height + 0.5, 0), 0xc2391e);
  addLabel(scene, "A", new THREE.Vector3(-halfBase, 0, -halfBase), 0xc2391e);
  addLabel(scene, "B", new THREE.Vector3(halfBase, 0, -halfBase), 0x4a4640);
  addLabel(scene, "C", new THREE.Vector3(halfBase, 0, halfBase), 0x4a4640);
  addLabel(scene, "D", new THREE.Vector3(-halfBase, 0, halfBase), 0x4a4640);

  // Add height indicator (SA)
  if (params.height) {
    addHeightIndicator(scene, new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, height, 0));
  }
}

function addLabel(scene: THREE.Scene, text: string, position: THREE.Vector3, color: number) {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d")!;
  canvas.width = 64;
  canvas.height = 32;

  context.fillStyle = `#${color.toString(16).padStart(6, "0")}`;
  context.font = "bold 20px JetBrains Mono, monospace";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(text, 32, 16);

  const texture = new THREE.CanvasTexture(canvas);
  const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(spriteMaterial);
  sprite.position.copy(position);
  sprite.scale.set(1, 0.5, 1);
  scene.add(sprite);
}

function addHeightIndicator(scene: THREE.Scene, from: THREE.Vector3, to: THREE.Vector3) {
  const geometry = new THREE.BufferGeometry().setFromPoints([from, to]);
  const material = new THREE.LineBasicMaterial({
    color: 0xc2391e,
    linewidth: 3,
    transparent: true,
    opacity: 0.8,
  });
  const line = new THREE.Line(geometry, material);
  scene.add(line);
}
