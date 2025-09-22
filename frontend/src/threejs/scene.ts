import * as THREE from 'three';

export function createBasicScene(container: HTMLElement) {
	const scene = new THREE.Scene();
	const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
	camera.position.set(1.5, 1.5, 1.5);
	const renderer = new THREE.WebGLRenderer({ antialias: true });
	renderer.setSize(container.clientWidth, container.clientHeight);
	container.appendChild(renderer.domElement);

	const light = new THREE.HemisphereLight(0xffffff, 0x444444, 1.2);
	scene.add(light);

	const onResize = () => {
		renderer.setSize(container.clientWidth, container.clientHeight);
		camera.aspect = container.clientWidth / container.clientHeight;
		camera.updateProjectionMatrix();
	};
	window.addEventListener('resize', onResize);

	return { scene, camera, renderer, dispose: () => {
		window.removeEventListener('resize', onResize);
		renderer.dispose();
		container.removeChild(renderer.domElement);
	}};
} 