import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

export const HelloWorld = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#0f172a',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <h1
        style={{
          color: 'white',
          fontSize: 72,
          opacity,
          fontFamily: 'sans-serif',
        }}
      >
        Healthcare Video
      </h1>
    </AbsoluteFill>
  );
};
