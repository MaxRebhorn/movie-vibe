import React from 'react';
import { motion } from 'framer-motion';
import styles from './ProgressBar.module.css';

const ProgressBar = ({ progress }) => {
  return (
    <div className={styles.progressContainer}>
      <div className={styles.progressHeader}>
        <span className="text-muted">
          {Math.round(progress)}% Complete
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
  );
};

export default ProgressBar;
