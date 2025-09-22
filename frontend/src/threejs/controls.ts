import type { PerspectiveCamera, Renderer } from 'three';

export async function createOrbitControls(camera: PerspectiveCamera, domElement: Renderer['domElement']) {
	const { OrbitControls } = await import('three/examples/jsm/controls/OrbitControls.js');
	const controls = new OrbitControls(camera, domElement);
	camera.position.set(2, 1.5, 2);
	controls.update();
	return controls;
} 