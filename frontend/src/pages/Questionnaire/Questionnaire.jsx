import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Navbar from "../../components/organisms/Navbar/Navbar";
import styles from "./Questionnaire.module.css";
import "../../styles/colors.css";

const questions = [
  {
    id: "vibe_party",
    title: "🎉 Wenn der Film eine Party wäre – welche Art?",
    options: ["Clubnacht", "Opernabend", "Lagerfeuer", "Leseabend", "Achterbahn"],
    type: "choice"
  },
  {
    id: "vibe_weather",
    title: "🌦️ Wenn der Film ein Wetter wäre – welches?",
    options: ["Sonne", "Gewitter", "Schnee", "Nebel", "Sturm"],
    type: "choice"
  },
  {
    id: "style_colors",
    title: "🎨 Welche Farben dominieren?",
    options: ["Blau", "Rot", "Schwarzweiß", "Bunt", "Erdig"],
    type: "multi"
  }
];

export default function Questionnaire() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [xp, setXp] = useState(0);
  const [xpPopup, setXpPopup] = useState(null);
  const userId = "user-123"; // später dynamisch

  const awardXp = (amount) => {
    setXp((prev) => prev + amount);
    setXpPopup({ id: Date.now(), amount });
    setTimeout(() => setXpPopup(null), 1000);
  };

  const handleSelect = (id, value) => {
    const q = questions[step];

    if (q.type === "multi") {
      const current = answers[id] || [];
      setAnswers({
        ...answers,
        [id]: current.includes(value) ? current.filter((v) => v !== value) : [...current, value]
      });
    } else {
      setAnswers({ ...answers, [id]: value });
      awardXp(5);
      setTimeout(() => setStep(step + 1), 600);
    }
  };

  const handleNextMulti = () => {
    awardXp(5);
    setStep(step + 1);
  };

  const handleFinish = async () => {
    const payload = { userId, answers, xp };
    try {
      await fetch("/api/submit-questionnaire", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      console.log("✅ Daten gesendet:", payload);
    } catch (err) {
      console.error("❌ API-Error:", err);
    }
  };

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
                className={styles.questionStep}
              >
                <h2 className={styles.questionTitle}>{currentQuestion.title}</h2>
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
                      onClick={() => handleSelect(currentQuestion.id, opt)}
                    >
                      {opt}
                    </motion.button>
                  ))}
                </div>

                {currentQuestion.type === "multi" && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={styles.nextButton}
                    onClick={handleNextMulti}
                  >
                    Weiter
                  </motion.button>
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
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className={styles.result}
              >
                <h2>✅ Fertig!</h2>
                <p>Du hast <strong>{xp} XP</strong> gesammelt 🎉</p>
                <pre>{JSON.stringify(answers, null, 2)}</pre>
                <button className={styles.nextButton} onClick={handleFinish}>
                  Ergebnisse senden
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Progressbar */}
        <div className={styles.progressContainer}>
          <div className={styles.progressHeader}>
            <span className={`${styles.progressLabel} text-muted`}>
              Frage {Math.min(step + 1, questions.length)} / {questions.length}
            </span>
            <span className={`${styles.progressPercent} text-primary`}>
              {Math.round(progress)}%
            </span>
          </div>
          <div className={styles.progressbar}>
            <motion.div
              className={styles.progressbarFill}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
