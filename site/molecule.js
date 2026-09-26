/* ==========================================================================
   Visualizador 3D real (Three.js, vendorizado — funciona 100% offline) do
   etanol, o produto final do processo. Ball-and-stick com coloracao CPK
   padrao (Carbono=cinza, Oxigenio=vermelho, Hidrogenio=branco), luz e
   sombra, arrastar para girar / scroll para zoom (OrbitControls).
========================================================================== */

const CPK_COLOR = { C: 0x4a4a4a, O: 0xe0342c, H: 0xf2f2f2 };
const ATOM_RADIUS = { C: 0.34, O: 0.38, H: 0.2 };

function buildMoleculeGroup(data) {
  const group = new THREE.Group();
  data.atoms.forEach((atom) => {
    const radius = ATOM_RADIUS[atom.el] || 0.3;
    const color = CPK_COLOR[atom.el] || 0x999999;
    const geo = new THREE.SphereGeometry(radius, 24, 18);
    const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.32, metalness: 0.12 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(atom.x, atom.y, atom.z);
    group.add(mesh);
  });
  data.bonds.forEach(([i, j]) => {
    const a = data.atoms[i], b = data.atoms[j];
    const start = new THREE.Vector3(a.x, a.y, a.z);
    const end = new THREE.Vector3(b.x, b.y, b.z);
    const mid = start.clone().add(end).multiplyScalar(0.5);
    const dir = end.clone().sub(start);
    const len = dir.length();
    const geo = new THREE.CylinderGeometry(0.1, 0.1, len, 12);
    const mat = new THREE.MeshStandardMaterial({ color: 0xd4d4d4, roughness: 0.45, metalness: 0.05 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.copy(mid);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
    group.add(mesh);
  });
  return group;
}

function initMoleculeScene() {
  const container = document.getElementById("molecule-stage");
  if (!container || typeof THREE === "undefined") {
    if (container) container.innerHTML = '<p style="color:#8b849b;font-size:0.85rem;padding:2rem;text-align:center;">Não foi possível carregar o visualizador 3D.</p>';
    return;
  }

  const width = container.clientWidth || 400;
  const height = container.clientHeight || 320;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
  camera.position.set(0, 0.6, 5.4);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  container.innerHTML = "";
  container.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const keyLight = new THREE.DirectionalLight(0xffffff, 1.0);
  keyLight.position.set(4, 6, 5);
  scene.add(keyLight);
  const rimLight = new THREE.DirectionalLight(0x8a6fd0, 0.55);
  rimLight.position.set(-5, -2, -4);
  scene.add(rimLight);

  const molecule = buildMoleculeGroup(MOLECULE_ETHANOL);
  scene.add(molecule);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 1.4;
  controls.enablePan = false;
  controls.minDistance = 3;
  controls.maxDistance = 10;

  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    const w = container.clientWidth, h = container.clientHeight;
    if (!w || !h) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });
}

initMoleculeScene();
