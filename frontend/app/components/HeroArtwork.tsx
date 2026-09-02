"use client";

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";

export function HeroArtwork() {
  const stageRef = useRef<HTMLDivElement>(null);
  const [motion, setMotion] = useState({ x: 0, y: 0 });
  const [entered, setEntered] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(true);

  useEffect(() => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setReduceMotion(prefersReduced);
    if (!prefersReduced) {
      const t = requestAnimationFrame(() => setEntered(true));
      return () => cancelAnimationFrame(t);
    }
    setEntered(true);
  }, []);

  const onPointerMove = useCallback(
    (e: React.PointerEvent<HTMLDivElement>) => {
      if (reduceMotion || !stageRef.current) return;
      const rect = stageRef.current.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width - 0.5;
      const py = (e.clientY - rect.top) / rect.height - 0.5;
      setMotion({ x: px * 5, y: py * 3 });
    },
    [reduceMotion],
  );

  const onPointerLeave = useCallback(() => {
    setMotion({ x: 0, y: 0 });
  }, []);

  return (
    <div
      ref={stageRef}
      className="hero-artwork-stage"
      onPointerMove={onPointerMove}
      onPointerLeave={onPointerLeave}
    >
      <div
        className={`hero-artwork-frame ${entered ? "hero-artwork-frame--visible" : ""}`}
        style={
          reduceMotion
            ? undefined
            : { transform: `translate3d(${motion.x}px, ${motion.y}px, 0)` }
        }
      >
        <Image
          src="/images/rework-hero.png"
          alt="RE:WORK journey from skills evidence through diagnosis and pathway to job readiness"
          width={1024}
          height={831}
          priority
          sizes="(max-width: 767px) 100vw, (max-width: 1280px) 52vw, 800px"
          className="hero-artwork-image"
        />
      </div>
    </div>
  );
}
