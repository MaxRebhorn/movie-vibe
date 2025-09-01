import React, {useState, useEffect} from "react";
import {motion, AnimatePresence} from "framer-motion";
import Navbar from "../../components/organisms/Navbar/Navbar";
import QuestionCard from "../../components/molecules/QuestionCard/QuestionCard";
import Button from "../../components/atoms/Button/Button";
import ProgressBar from "../../components/atoms/ProgressBar/ProgressBar";
import styles from "./Questionnaire.module.css";
import "../../styles/colors.css";
import {movieAPI, questionnaireAPI} from "../../services/api";
import noviceQuestions from "../../data/novice_questions.json";
import proQuestions from "../../data/pro_questions.json";
import { useParams } from "react-router-dom";

export default function Questionnaire() {
    const { id: movieId } = useParams();
    const [questionSet, setQuestionSet] = useState("novice");
    const [questions, setQuestions] = useState([]);
    const [step, setStep] = useState(0);
    const [answers, setAnswers] = useState({});
    const [xp, setXp] = useState(0);
    const [xpPopup, setXpPopup] = useState(null);
    const [movieResults, setMovieResults] = useState([]);

    // Hardcoded user ID for testing - remove this in production!
    const userId = "test-user-123";
    const isDebugMode = true; // Set to false in production

    const xpPerSet = {
        novice: 5,
        pro: 10,
    };

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
        setXpPopup({id: Date.now(), amount});
        setTimeout(() => setXpPopup(null), 1000);
    };

    const handleSelect = async (id, value, type, vector_type = null) => {
        if (type === "movie_input") {
            setAnswers({...answers, [id]: value});
            if (!value) return setMovieResults([]);
            const res = await movieAPI.search(value);
            setMovieResults(res || []);
            return;
        }

        if (type === "multi") {
            const current = answers[id]?.values || [];
            setAnswers({
                ...answers,
                [id]: {
                    values: current.includes(value)
                        ? current.filter((v) => v !== value)
                        : [...current, value],
                    vector_type: vector_type || answers[id]?.vector_type || null
                }
            });
        } else {
            setAnswers({...answers, [id]: value});
            if (type === "choice") {
                awardXp(xpPerSet[questionSet]);
                setTimeout(() => setStep((prev) => prev + 1), 300);
            }
        }
    };

    const handleTextChange = (id, value) => {
        setAnswers({...answers, [id]: value});
    };

    const handleMovieSelect = (title) => {
        setAnswers({...answers, most_similar_movie: title});
        setMovieResults([]);
    };

    const handleNext = () => {
        awardXp(xpPerSet[questionSet]);
        setStep((prev) => prev + 1);
        window.scrollTo({top: 0, behavior: "smooth"});
    };

    const handleFinish = async () => {
        // For testing: include user ID in payload
        const payload = isDebugMode
            ? { answers, debug_user_id: userId, xp }
            : { answers };

        try {
            await questionnaireAPI.submitQuestionnaire(movieId, payload);
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
            <Navbar/>
            <div className={styles.questionnaireContainer}>
                <div className={styles.card}>
                    <AnimatePresence mode="wait">
                        {currentQuestion ? (
                            <motion.div
                                key={currentQuestion.id}
                                initial={{opacity: 0, y: 20}}
                                animate={{opacity: 1, y: 0}}
                                exit={{opacity: 0, y: -20}}
                                transition={{duration: 0.3}}
                                style={{position: "relative"}}
                            >
                                <QuestionCard
                                    question={currentQuestion}
                                    answers={answers}
                                    onSelect={(id, value, type) => handleSelect(id, value, type, currentQuestion.vector_type)}
                                    onTextChange={handleTextChange}
                                    movieResults={movieResults}
                                    onMovieSelect={handleMovieSelect}
                                />

                                {["multi", "text", "movie_select"].includes(
                                    currentQuestion.type
                                ) && (
                                    <Button
                                        variant="primary"
                                        onClick={handleNext}
                                        disabled={
                                            (currentQuestion.type === "multi" &&
                                                (!answers[currentQuestion.id] ||
                                                    answers[currentQuestion.id].length === 0)) ||
                                            (["text", "movie_select"].includes(
                                                    currentQuestion.type
                                                ) &&
                                                !answers[currentQuestion.id])
                                        }
                                        className={styles.submitButton}
                                    >
                                        Weiter
                                    </Button>
                                )}
                            </motion.div>
                        ) : (
                            <motion.div
                                initial={{opacity: 0, scale: 0.95}}
                                animate={{opacity: 1, scale: 1}}
                                exit={{opacity: 0}}
                                className={styles.completionContainer}
                            >
                                <h2>Vielen Dank!</h2>
                                <p>
                                    Du hast <strong>{xp}</strong> XP gesammelt.
                                </p>

                                {questionSet === "novice" ? (
                                    <>
                                        <p>
                                            Wenn du möchtest, kannst du noch detailliertere Fragen
                                            beantworten, um das beste Ergebnis zu erhalten.
                                        </p>
                                        <Button
                                            variant="primary"
                                            onClick={() => setQuestionSet("pro")}
                                            className={styles.nextButton}
                                        >
                                            Und jetzt noch etwas genauer
                                        </Button>
                                    </>
                                ) : (
                                    <p>Du hast nun das Profi-Questionnaire abgeschlossen.</p>
                                )}

                                <Button variant="primary" onClick={handleFinish}>
                                    Fertig
                                </Button>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* XP-Popup */}
                    <AnimatePresence>
                        {xpPopup && (
                            <motion.div
                                key={xpPopup.id}
                                className={styles.xpPopup}
                                initial={{opacity: 0, y: 0}}
                                animate={{opacity: 1, y: -50}}
                                exit={{opacity: 0, y: -80}}
                                transition={{duration: 1}}
                            >
                                +{xpPopup.amount} XP
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <ProgressBar progress={progress}/>
            </div>
        </div>
    );
}