import React from 'react';
import { motion } from 'framer-motion';
import Button from '../../atoms/Button/Button';
import styles from './QuestionCard.module.css';

const QuestionCard = ({ 
  question, 
  answers, 
  onSelect, 
  onTextChange, 
  movieResults = [], 
  onMovieSelect 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -40 }}
      transition={{ duration: 0.4 }}
      className={styles.card}
    >
      <h2 className={styles.questionTitle}>{question.title}</h2>

      {['choice', 'multi'].includes(question.type) && (
        <div className={styles.options}>
          {question.options.map((opt) => (
            <Button
              key={opt}
              variant="option"
              className={`${styles.optionButton} ${
                (Array.isArray(answers[question.id])
                  ? answers[question.id].includes(opt)
                  : answers[question.id] === opt)
                  ? styles.selected : ''
              }`}
              onClick={() => onSelect(question.id, opt, question.type)}
            >
              {opt}
            </Button>
          ))}
        </div>
      )}

      {question.type === 'text' && (
        <textarea
          className={styles.textInput}
          value={answers[question.id] || ''}
          onChange={(e) => onTextChange(question.id, e.target.value)}
        />
      )}

      {question.type === 'movie_select' && (
        <div className={styles.autocompleteContainer}>
          <input
            className={styles.autocompleteInput}
            value={answers[question.id] || ''}
            onChange={(e) => onSelect(question.id, e.target.value, 'movie_input')}
            placeholder="Filmtitel eingeben..."
          />
          {movieResults.length > 0 && (
            <div className={styles.autocompleteDropdown}>
              {movieResults.map((movie) => (
                <div
                  key={movie.id}
                  className={styles.autocompleteItem}
                  onClick={() => onMovieSelect(movie.title)}
                >
                  {movie.title}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default QuestionCard;
