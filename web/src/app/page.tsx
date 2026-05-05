'use client';

import { motion } from 'framer-motion';
import Header from './components/Header';
import DecorativeBlobs from './components/DecorativeBlobs';
import SceneSelector from './components/SceneSelector';
import SourceInput from './components/SourceInput';
import CharacterGrid from './components/CharacterGrid';
import StyleSelector from './components/StyleSelector';
import NewsModeHint from './components/NewsModeHint';
import SubmitButton from './components/SubmitButton';
import ProgressBar from './components/ProgressBar';
import ResultCard from './components/ResultCard';
import Footer from './components/Footer';
import { useAnimation } from './hooks/useAnimation';

export default function Home() {
  const {
    sceneMode,
    source,
    sourceType,
    character,
    characterCount,
    style,
    loading,
    progress,
    statusText,
    result,
    setSceneMode,
    setSource,
    setSourceType,
    setCharacter,
    setCharacterCount,
    setStyle,
    handleSubmit,
    handleReset,
  } = useAnimation();

  return (
    <main className="min-h-screen" style={{ background: '#fef9f0' }}>
      {/* Decorative gradient blobs */}
      <DecorativeBlobs />

      <div className="relative max-w-2xl mx-auto px-5 py-12 md:py-16">
        <Header />

        <SceneSelector sceneMode={sceneMode} onChange={setSceneMode} />
        <SourceInput
          source={source}
          sourceType={sourceType}
          sceneMode={sceneMode}
          onChange={setSource}
          onTypeChange={setSourceType}
        />

        {/* Character & Scene-specific sections */}
        {sceneMode !== 'news' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-8 overflow-hidden"
          >
            <CharacterGrid
              character={character}
              characterCount={characterCount}
              sceneMode={sceneMode}
              onCharacterChange={setCharacter}
              onCountChange={setCharacterCount}
            />
          </motion.div>
        )}

        {sceneMode === 'news' && <NewsModeHint />}

        {sceneMode === 'dialogue' && (
          <StyleSelector style={style} onChange={setStyle} />
        )}

        <SubmitButton
          loading={loading}
          disabled={loading || !source.trim()}
          onClick={handleSubmit}
        />

        <ProgressBar loading={loading} progress={progress} statusText={statusText} />
        <ResultCard result={result} onReset={handleReset} />
        <Footer />
      </div>
    </main>
  );
}
