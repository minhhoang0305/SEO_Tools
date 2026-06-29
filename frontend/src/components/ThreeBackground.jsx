import { useEffect, useRef } from 'react';
import * as THREE from 'three';

const palettes = {
  audit: {
    primary: '#38bdf8',
    secondary: '#22c55e',
    mesh: '#0f766e',
  },
  submit: {
    primary: '#a78bfa',
    secondary: '#f472b6',
    mesh: '#7c3aed',
  },
  auth: {
    primary: '#60a5fa',
    secondary: '#f59e0b',
    mesh: '#2563eb',
  },
};

export default function ThreeBackground({ variant = 'submit' }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return undefined;

    const colors = palettes[variant] ?? palettes.submit;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 0, 8);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    renderer.setSize(window.innerWidth, window.innerHeight);
    mount.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    const geometry = new THREE.TorusKnotGeometry(1.7, 0.42, 180, 18);
    const material = new THREE.MeshBasicMaterial({
      color: colors.mesh,
      wireframe: true,
      transparent: true,
      opacity: 0.22,
    });
    const knot = new THREE.Mesh(geometry, material);
    knot.position.set(2.8, -0.4, -1.2);
    knot.rotation.set(0.6, 0.3, 0.2);
    group.add(knot);

    const particles = 520;
    const positions = new Float32Array(particles * 3);
    for (let i = 0; i < particles; i += 1) {
      positions[i * 3] = (Math.random() - 0.5) * 15;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 9;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 7;
    }
    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMaterial = new THREE.PointsMaterial({
      color: colors.primary,
      size: 0.018,
      transparent: true,
      opacity: 0.65,
    });
    const pointCloud = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(pointCloud);

    const ringGeometry = new THREE.RingGeometry(2.3, 2.33, 96);
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: colors.secondary,
      transparent: true,
      opacity: 0.16,
      side: THREE.DoubleSide,
    });
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.position.set(-3.4, 1.3, -1.6);
    ring.rotation.set(0.9, 0.2, -0.4);
    scene.add(ring);

    let frame = 0;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      knot.rotation.x += 0.0028;
      knot.rotation.y += 0.0035;
      ring.rotation.z += 0.0018;
      pointCloud.rotation.y += 0.0008;
      pointCloud.rotation.x = Math.sin(Date.now() * 0.00018) * 0.08;
      renderer.render(scene, camera);
    };

    const resize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', resize);
    animate();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
      mount.removeChild(renderer.domElement);
      geometry.dispose();
      material.dispose();
      particleGeometry.dispose();
      particleMaterial.dispose();
      ringGeometry.dispose();
      ringMaterial.dispose();
      renderer.dispose();
    };
  }, [variant]);

  return <div ref={mountRef} className="three-bg" aria-hidden="true" />;
}
