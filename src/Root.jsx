import { Composition } from 'remotion';
import { HelloWorld } from './HelloWorld';

export const RemotionRoot = () => {
  return (
    <Composition
      id="HelloWorld"
      component={HelloWorld}
      durationInFrames={150}
      fps={30}
      width={1280}
      height={720}
    />
  );
};
