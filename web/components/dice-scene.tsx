"use client"

import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { Environment, Float, RoundedBox, MeshTransmissionMaterial, ContactShadows, Lightformer } from "@react-three/drei"
import { useRef, useMemo, useEffect, useState } from "react"
import * as THREE from "three"

// --- CONFIGURATION ---
const DIE_SIZE = 2
const PIP_RADIUS = 0.15
const PIP_SPREAD = 0.55
const PIP_DEPTH = 1.0 - PIP_RADIUS + 0.05

const SMOKED_GLASS_MATERIAL = {
    backside: true,
    samples: 16,
    resolution: 1024,
    transmission: 1,
    roughness: 0,
    thickness: 1.5,
    ior: 1.5,
    chromaticAberration: 0.06,
    anisotropy: 0.1,
    distortion: 0.1,
    distortionScale: 0.2,
    temporalDistortion: 0,
    clearcoat: 1,
    attenuationDistance: 0.75,
    attenuationColor: "#ffffff",
    color: "#202020",
    bg: "#ffffff"
}

function Pips() {
    const material = useMemo(() => new THREE.MeshStandardMaterial({
        color: "#ffffff",
        roughness: 0,
        emissive: "#ffffff",
        emissiveIntensity: 1.5,
        toneMapped: false
    }), [])

    const Pip = ({ pos }: { pos: [number, number, number] }) => (
        <mesh position={pos}>
            <sphereGeometry args={[PIP_RADIUS, 32, 32]} />
            <primitive object={material} />
        </mesh>
    )

    const Face = ({ children, rotation = [0, 0, 0] }: { children: React.ReactNode; rotation?: [number, number, number] }) => (
        <group rotation={rotation}>{children}</group>
    )

    return (
        <group>
            {/* 1 - Front */}
            <Face>
                <Pip pos={[0, 0, PIP_DEPTH]} />
            </Face>

            {/* 6 - Back */}
            <Face rotation={[0, Math.PI, 0]}>
                <Pip pos={[-PIP_SPREAD, -PIP_SPREAD, PIP_DEPTH]} /><Pip pos={[-PIP_SPREAD, 0, PIP_DEPTH]} /><Pip pos={[-PIP_SPREAD, PIP_SPREAD, PIP_DEPTH]} />
                <Pip pos={[PIP_SPREAD, -PIP_SPREAD, PIP_DEPTH]} /><Pip pos={[PIP_SPREAD, 0, PIP_DEPTH]} /><Pip pos={[PIP_SPREAD, PIP_SPREAD, PIP_DEPTH]} />
            </Face>

            {/* 2 - Top */}
            <Face rotation={[-Math.PI / 2, 0, 0]}>
                <Pip pos={[-PIP_SPREAD, -PIP_SPREAD, PIP_DEPTH]} />
                <Pip pos={[PIP_SPREAD, PIP_SPREAD, PIP_DEPTH]} />
            </Face>

            {/* 5 - Bottom */}
            <Face rotation={[Math.PI / 2, 0, 0]}>
                <Pip pos={[-PIP_SPREAD, -PIP_SPREAD, PIP_DEPTH]} /><Pip pos={[PIP_SPREAD, PIP_SPREAD, PIP_DEPTH]} />
                <Pip pos={[-PIP_SPREAD, PIP_SPREAD, PIP_DEPTH]} /><Pip pos={[PIP_SPREAD, -PIP_SPREAD, PIP_DEPTH]} />
                <Pip pos={[0, 0, PIP_DEPTH]} />
            </Face>

            {/* 3 - Right */}
            <Face rotation={[0, Math.PI / 2, 0]}>
                <Pip pos={[-PIP_SPREAD, -PIP_SPREAD, PIP_DEPTH]} />
                <Pip pos={[0, 0, PIP_DEPTH]} />
                <Pip pos={[PIP_SPREAD, PIP_SPREAD, PIP_DEPTH]} />
            </Face>

            {/* 4 - Left */}
            <Face rotation={[0, -Math.PI / 2, 0]}>
                <Pip pos={[-PIP_SPREAD, -PIP_SPREAD, PIP_DEPTH]} /><Pip pos={[PIP_SPREAD, PIP_SPREAD, PIP_DEPTH]} />
                <Pip pos={[-PIP_SPREAD, PIP_SPREAD, PIP_DEPTH]} /><Pip pos={[PIP_SPREAD, -PIP_SPREAD, PIP_DEPTH]} />
            </Face>
        </group>
    )
}

// Mouse tracking for interactivity
function MouseTracker({ onMouseMove }: { onMouseMove: (x: number, y: number) => void }) {
    const { viewport } = useThree()

    useEffect(() => {
        const handleMouseMove = (event: MouseEvent) => {
            const x = (event.clientX / window.innerWidth) * 2 - 1
            const y = -(event.clientY / window.innerHeight) * 2 + 1
            onMouseMove(x * viewport.width * 0.1, y * viewport.height * 0.1)
        }

        window.addEventListener('mousemove', handleMouseMove)
        return () => window.removeEventListener('mousemove', handleMouseMove)
    }, [onMouseMove, viewport])

    return null
}

function CrystalDie() {
    const meshRef = useRef<THREE.Group>(null)
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
    const targetRotation = useRef({ x: 0, y: 0 })

    useFrame((state) => {
        if (!meshRef.current) return
        const t = state.clock.getElapsedTime()

        // Smooth mouse influence
        targetRotation.current.x = mousePos.y * 0.3
        targetRotation.current.y = mousePos.x * 0.3

        // Base rotation + subtle mouse influence
        meshRef.current.rotation.x = Math.sin(t * 0.2) * 0.2 + targetRotation.current.x * 0.4
        meshRef.current.rotation.y = t * 0.25 + targetRotation.current.y * 0.4
        meshRef.current.rotation.z = Math.cos(t * 0.2) * 0.1
    })

    return (
        <>
            <MouseTracker onMouseMove={(x, y) => setMousePos({ x, y })} />
            <Float speed={2} rotationIntensity={0.5} floatIntensity={1} floatingRange={[-0.2, 0.2]}>
                <group ref={meshRef}>
                    {/* The Glass Box */}
                    <RoundedBox args={[DIE_SIZE, DIE_SIZE, DIE_SIZE]} radius={0.25} smoothness={8}>
                        <MeshTransmissionMaterial {...SMOKED_GLASS_MATERIAL} />
                    </RoundedBox>

                    {/* The White Dots */}
                    <Pips />
                </group>
            </Float>
        </>
    )
}

export function DiceScene() {
    return (
        <Canvas dpr={[1, 2]} camera={{ position: [0, 1, 6], fov: 45 }}>
            {/* Light background to match minimalist theme */}
            <color attach="background" args={["#fafafa"]} />

            <Environment resolution={512}>
                <group rotation={[-Math.PI / 3, 0, 1]}>
                    <Lightformer form="rect" intensity={5} position={[3, 4, 3]} scale={5} color="#ffffff" />
                    <Lightformer form="rect" intensity={3} position={[-5, 0, -5]} scale={5} color="#ffffff" />
                    <Lightformer form="circle" intensity={2} position={[0, 5, 0]} scale={2} color="#ffffff" />
                </group>
            </Environment>

            <CrystalDie />

            <ContactShadows
                position={[0, -1.6, 0]}
                opacity={0.6}
                scale={15}
                blur={2.5}
                far={4}
            />
        </Canvas>
    )
}