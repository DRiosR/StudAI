'use client';

import { useEffect, useState } from 'react';

interface WordPair {
  word: string;
  translation: string;
}

const WORDS: WordPair[] = [
  { word: 'apple', translation: 'manzana' },
  { word: 'house', translation: 'casa' },
  { word: 'water', translation: 'agua' },
  { word: 'sun', translation: 'sol' },
  { word: 'moon', translation: 'luna' },
  { word: 'star', translation: 'estrella' },
  { word: 'tree', translation: 'árbol' },
  { word: 'book', translation: 'libro' },
  { word: 'dog', translation: 'perro' },
  { word: 'cat', translation: 'gato' },
  { word: 'school', translation: 'escuela' },
  { word: 'friend', translation: 'amigo' },
  { word: 'music', translation: 'música' },
  { word: 'love', translation: 'amor' },
  { word: 'river', translation: 'río' },
  { word: 'mountain', translation: 'montaña' },
  { word: 'sky', translation: 'cielo' },
  { word: 'coffee', translation: 'café' },
  { word: 'computer', translation: 'computadora' },
  { word: 'flower', translation: 'flor' },
  { word: 'happy', translation: 'feliz' },
  { word: 'sad', translation: 'triste' },
  { word: 'light', translation: 'luz' },
  { word: 'dark', translation: 'oscuro' },
  { word: 'red', translation: 'rojo' },
  { word: 'blue', translation: 'azul' },
  { word: 'green', translation: 'verde' },
  { word: 'yellow', translation: 'amarillo' },
  { word: 'black', translation: 'negro' },
  { word: 'white', translation: 'blanco' },
  { word: 'beach', translation: 'playa' },
  { word: 'snow', translation: 'nieve' },
  { word: 'rain', translation: 'lluvia' },
  { word: 'time', translation: 'tiempo' },
  { word: 'world', translation: 'mundo' },
  { word: 'family', translation: 'familia' },
  { word: 'dream', translation: 'sueño' },
  { word: 'smile', translation: 'sonrisa' },
  { word: 'heart', translation: 'corazón' },
];

function shuffleWord(word: string) {
  const arr = word.split('');
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr.join('');
}

export default function UnscrambleGame() {
  const [index, setIndex] = useState(0);
  const [scrambled, setScrambled] = useState('');
  const [input, setInput] = useState('');
  const [score, setScore] = useState(0);
  const [message, setMessage] = useState('');
  const [showTranslation, setShowTranslation] = useState(false);
  const [gameOver, setGameOver] = useState(false);

  useEffect(() => {
    const currentWord = WORDS[index].word;
    let scrambledWord = shuffleWord(currentWord);
    // prevent same as original
    while (scrambledWord === currentWord) scrambledWord = shuffleWord(currentWord);
    setScrambled(scrambledWord);
    setInput('');
    setMessage('');
    setShowTranslation(false);
  }, [index]);

  const handleSubmit = () => {
    const currentWord = WORDS[index].word;
    if (input.trim().toLowerCase() === currentWord.toLowerCase()) {
      setScore((s) => s + 1);
      setMessage('✅ Correct!');
      setTimeout(() => {
        if (index + 1 < WORDS.length) setIndex((i) => i + 1);
        else setGameOver(true);
      }, 700);
    } else {
      setMessage('❌ Try again!');
    }
  };

  const restartGame = () => {
    setIndex(0);
    setScore(0);
    setGameOver(false);
  };

  if (gameOver) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px] text-center text-white">
        <h1 className="text-2xl font-bold mb-4">🎉 Game Over!</h1>
        <p className="text-lg mb-2">Final Score: {score}/{WORDS.length}</p>
        <button
          onClick={restartGame}
          className="px-4 py-2 mt-4 bg-purple-600 hover:bg-purple-700 rounded-lg transition"
        >
          Play Again
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center text-center text-white min-h-[320px]">
      <h2 className="text-xl font-semibold mb-2">Unscramble the Word</h2>
      <p className="text-purple-400 mb-4">Score: {score}</p>

      <div className="text-4xl font-bold mb-4 tracking-wider">{scrambled}</div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        placeholder="Type your answer"
        className="text-black px-3 py-2 rounded-lg outline-none border border-gray-300"
      />

      <button
        onClick={handleSubmit}
        className="px-4 py-2 mt-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition"
      >
        Check
      </button>

      {message && <p className="mt-3 text-lg">{message}</p>}

      <button
        onClick={() => setShowTranslation((v) => !v)}
        className="text-sm mt-4 underline text-white/70 hover:text-white"
      >
        {showTranslation ? 'Hide' : 'Show'} translation
      </button>

      {showTranslation && (
        <p className="text-yellow-400 mt-2">
          {WORDS[index].translation}
        </p>
      )}

      <p className="text-xs text-white/50 mt-6">
        Word {index + 1} of {WORDS.length}
      </p>
    </div>
  );
}
