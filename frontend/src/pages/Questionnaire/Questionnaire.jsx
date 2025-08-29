import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Navbar from "../../components/organisms/Navbar/Navbar";
import styles from "./Questionnaire.module.css";
import "../../styles/colors.css";
import { movieAPI } from "../../services/api";
import noviceQuestions from "../../data/novice_questions.json";
import proQuestions from "../../data/pro_questions.json";
export default function Questionnaire() {
  const [questionSet, setQuestionSet] = useState("novice"); // novice | pro
  const [questions, setQuestions] = useState([]);
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [xp, setXp] = useState(0);
  const [xpPopup, setXpPopup] = useState(null);
  const [movieResults, setMovieResults] = useState([]);
  const userId = "user-123"; // später dynamisch

  // Lade das richtige JSON basierend auf dem Set
  useEffect(() => {
  if (questionSet === "novice") {
    setQuestions(noviceQuestions);
  } else {
    setQuestions(proQuestions);
  }
  setStep(0);
  setAnswers({});
}, [questionSet]);


  const awardXp = (amount) => {
    setXp((prev) => prev + amount);
    setXpPopup({ id: Date.now(), amount });
    setTimeout(() => setXpPopup(null), 1000);
  };

  const handleSelect = (id, value, type) => {
    if (type === "multi") {
      const current = answers[id] || [];
      setAnswers({
        ...answers,
        [id]: current.includes(value)
          ? current.filter((v) => v !== value)
          : [...current, value],
      });
    } else {
      setAnswers({ ...answers, [id]: value });
      // Choice Fragen gehen sofort weiter
      if (type === "choice") {
        awardXp(5);
        setTimeout(() => setStep(step + 1), 300);
      }
    }
  };

  const handleTextChange = (id, value) =>
    setAnswers({ ...answers, [id]: value });

  const handleMovieInput = async (query) => {
    setAnswers({ ...answers, most_similar_movie: query });
    if (!query) return setMovieResults([]);
    const res = await movieAPI.search(query);
    setMovieResults(res || []);
  };

  const selectMovie = (title) => {
    setAnswers({ ...answers, most_similar_movie: title });
    setMovieResults([]);
  };

  const handleNext = () => {
    awardXp(5);
    setStep(step + 1);
  };

  const handleFinish = async () => {
    const payload = { userId, answers, xp };
    try {
      await fetch("/api/submit-questionnaire", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      console.log("Daten gesendet:", payload);
    } catch (err) {
      console.error("API-Error:", err);
    }
  };

  if (!questions.length) return null;
  const currentQuestion = questions[step];
  const progress = (step / questions.length) * 100;

  return (
    <div className={styles.container}>
      <Navbar />
      <div className={styles.questionnaireContainer}>
        <div className={styles.card}>
          <AnimatePresence mode="wait">
            {currentQuestion ? (
              <motion.div
                key={currentQuestion.id}
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -40 }}
                transition={{ duration: 0.4 }}
              >
                <h2 className={styles.questionTitle}>{currentQuestion.title}</h2>

                {/* Choice / Multi */}
                {["choice", "multi"].includes(currentQuestion.type) && (
                  <div className={styles.options}>
                    {currentQuestion.options.map((opt) => (
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        key={opt}
                        className={`${styles.optionButton} ${
                          (Array.isArray(answers[currentQuestion.id])
                            ? answers[currentQuestion.id].includes(opt)
                            : answers[currentQuestion.id] === opt)
                            ? styles.selected
                            : ""
                        }`}
                        onClick={() =>
                          handleSelect(
                            currentQuestion.id,
                            opt,
                            currentQuestion.type
                          )
                        }
                      >
                        {opt}
                      </motion.button>
                    ))}
                  </div>
                )}

                {/* Text */}
                {currentQuestion.type === "text" && (
                  <>
                    <textarea
                      className={styles.textInput}
                      value={answers[currentQuestion.id] || ""}
                      onChange={(e) =>
                        handleTextChange(currentQuestion.id, e.target.value)
                      }
                    />
                  </>
                )}

                {/* Movie Autocomplete */}
                {currentQuestion.type === "movie_select" && (
                  <>
                    <div className={styles.autocompleteContainer}>
                      <input
                        className={styles.autocompleteInput}
                        value={answers[currentQuestion.id] || ""}
                        onChange={(e) => handleMovieInput(e.target.value)}
                        placeholder="Filmtitel eingeben..."
                      />
                      {movieResults.length > 0 && (
                        <div className={styles.autocompleteDropdown}>
                          {movieResults.map((movie) => (
                            <div
                              key={movie.id}
                              className={styles.autocompleteItem}
                              onClick={() => selectMovie(movie.title)}
                            >
                              {movie.title}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </>
                )}

                {/* Weiter Button */}
                {["multi", "text", "movie_select"].includes(
                  currentQuestion.type
                ) && (
                  <button
                    className={styles.submitButton}
                    onClick={handleNext}
                    disabled={
                      (currentQuestion.type === "multi" &&
                        (!answers[currentQuestion.id] ||
                          answers[currentQuestion.id].length === 0)) ||
                      (["text", "movie_select"].includes(currentQuestion.type) &&
                        !answers[currentQuestion.id])
                    }
                  >
                    Weiter
                  </button>
                )}

                {/* XP Popup */}
                <AnimatePresence>
                  {xpPopup && (
                    <motion.div
                      key={xpPopup.id}
                      className={styles.xpPopup}
                      initial={{ opacity: 0, y: 0 }}
                      animate={{ opacity: 1, y: -50 }}
                      exit={{ opacity: 0, y: -80 }}
                      transition={{ duration: 1 }}
                    >
                      +{xpPopup.amount} XP
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ) : (
                <motion.div
                    initial={{opacity: 0, scale: 0.9}}
                    animate={{opacity: 1, scale: 1}}
                >
                  <h2>Vielen Dank!</h2>
                  <p>Du hast <strong>{xp}</strong> XP gesammelt.</p>

                  {questionSet === "novice" ? (
                      <>
                        <p>Wenn du möchtest, kannst du noch detailliertere Fragen beantworten, um das beste Ergebnis zu
                          erhalten.</p>
                        <button
                            className={styles.nextButton}
                            onClick={() => setQuestionSet("pro")}
                        >
                          Und jetzt noch etwas genauer
                        </button>
                      </>
                  ) : (
                      <p>Du hast nun das Profi-Questionnaire abgeschlossen.</p>
                  )}

                  <button className={styles.nextButton} >
                    Fertig
                  </button>
                </motion.div>

            )}
          </AnimatePresence>
        </div>

        {/* Progressbar */}
        <div className={styles.progressContainer}>
          <div className={styles.progressHeader}>
            <span className="text-muted">
              Frage {Math.min(step + 1, questions.length)} / {questions.length}
            </span>
            <span className="text-primary">{Math.round(progress)}%</span>
          </div>
          <div className={styles.progressbar}>
            <motion.div
                className={styles.progressbarFill}
                initial={{width: 0}}
                animate={{width: `${progress}%`}}
                transition={{duration: 0.6, ease: "easeOut"}}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
