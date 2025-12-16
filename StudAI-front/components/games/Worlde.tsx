'use client';

import { useEffect, useState } from 'react';

const WORDS = [
  'apple', 'water', 'beach', 'music', 'world',
  'cielo', 'luz', 'flor', 'tiempo', 'familia',
  'dream', 'heart', 'river', 'green', 'smile',
  'rojo', 'azul', 'negro', 'blanco', 'feliz',
  'sunny', 'cloud', 'amigo', 'lluvia', 'nieve',
  'house', 'mount', 'perro', 'gato', 'libro',
  'coffee', 'moon', 'estre', 'playa', 'coraz',
  'mundo', 'sueño', 'flore', 'amour', 'tierr'
];

type LetterStatus = 'correct' | 'present' | 'absent' | '';

export default function WordleGame() {
  const [targetWord, setTargetWord] = useState('');
  const [guesses, setGuesses] = useState<string[]>([]);
  const [currentGuess, setCurrentGuess] = useState('');
  const [message, setMessage] = useState('');
  const [gameOver, setGameOver] = useState(false);

  useEffect(() => {
    const randomWord = WORDS[Math.floor(Math.random() * WORDS.length)].toLowerCase();
    setTargetWord(randomWord);
  }, []);

  const checkGuess = (guess: string): LetterStatus[] => {
    const statuses: LetterStatus[] = Array(guess.length).fill('');
    const targetArr = targetWord.split('');

    // First pass: correct positions
    guess.split('').forEach((ch, i) => {
      if (ch === targetArr[i]) {
        statuses[i] = 'correct';
        targetArr[i] = '_'; // mark used
      }
    });

    // Second pass: present elsewhere
    guess.split('').forEach((ch, i) => {
      if (statuses[i] === '' && targetArr.includes(ch)) {
        statuses[i] = 'present';
        targetArr[targetArr.indexOf(ch)] = '_';
      } else if (statuses[i] === '') {
        statuses[i] = 'absent';
      }
    });

    return statuses;
  };

  const handleSubmit = () => {
    if (currentGuess.length !== targetWord.length) {
      setMessage(`Use exactly ${targetWord.length} letters.`);
      return;
    }
    const newGuesses = [...guesses, currentGuess.toLowerCase()];
    setGuesses(newGuesses);

    if (currentGuess.toLowerCase() === targetWord) {
      setMessage('🎉 Correct!');
      setGameOver(true);
    } else if (newGuesses.length >= 6) {
      setMessage(`💀 The word was: ${targetWord.toUpperCase()}`);
      setGameOver(true);
    } else {
      setMessage('');
    }
    setCurrentGuess('');
  };

  const restartGame = () => {
    const newWord = WORDS[Math.floor(Math.random() * WORDS.length)].toLowerCase();
    setTargetWord(newWord);
    setGuesses([]);
    setCurrentGuess('');
    setGameOver(false);
    setMessage('');
  };

  return (
    <div className="flex flex-col items-center text-center text-white min-h-[320px]">
      <h1 className="text-xl font-bold mb-2">Wordle — English & Español</h1>
      <p className="text-purple-400 mb-3">Guess the {targetWord.length}-letter word</p>

      <div className="space-y-2 mb-3">
        {guesses.map((g, idx) => (
          <WordRow key={idx} word={g} target={targetWord} />
        ))}
        {!gameOver && guesses.length < 6 && (
          <input
            value={currentGuess}
            onChange={(e) => setCurrentGuess(e.target.value.toLowerCase())}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            maxLength={targetWord.length}
            className="text-black px-3 py-2 rounded-md outline-none border border-gray-300 text-center tracking-widest uppercase"
            placeholder="Type guess"
          />
        )}
      </div>

      {message && <p className="mt-2 text-sm">{message}</p>}

      {gameOver && (
        <button
          onClick={restartGame}
          className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition"
        >
          Play Again
        </button>
      )}
    </div>
  );
}

function WordRow({ word, target }: { word: string; target: string }) {
  const statuses = checkStatuses(word, target);

  return (
    <div className="flex justify-center gap-1">
      {word.split('').map((ch, i) => (
        <div
          key={i}
          className={`w-8 h-8 flex items-center justify-center font-bold text-lg rounded-md
            ${statuses[i] === 'correct' ? 'bg-green-500' :
              statuses[i] === 'present' ? 'bg-yellow-500' :
              'bg-gray-600'}`}
        >
          {ch.toUpperCase()}
        </div>
      ))}
    </div>
  );
}

function checkStatuses(guess: string, target: string): LetterStatus[] {
  const statuses: LetterStatus[] = Array(guess.length).fill('');
  const targetArr = target.split('');

  guess.split('').forEach((ch, i) => {
    if (ch === targetArr[i]) {
      statuses[i] = 'correct';
      targetArr[i] = '_';
    }
  });

  guess.split('').forEach((ch, i) => {
    if (statuses[i] === '' && targetArr.includes(ch)) {
      statuses[i] = 'present';
      targetArr[targetArr.indexOf(ch)] = '_';
    } else if (statuses[i] === '') {
      statuses[i] = 'absent';
    }
  });

  return statuses;
}
