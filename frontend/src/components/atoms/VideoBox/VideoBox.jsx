import React from "react";
import styles from "./VideoBox.module.css";

/**
 * Converts a YouTube URL (watch or short) into an embed URL.
 */
const toEmbedUrl = (url) => {
  try {
    const urlObj = new URL(url.startsWith("http") ? url : "https://" + url);

    // Short URL: youtu.be/VIDEO_ID
    if (urlObj.hostname.includes("youtu.be")) {
      return `https://www.youtube.com/embed/${urlObj.pathname.slice(1)}`;
    }

    // Standard watch URL: youtube.com/watch?v=VIDEO_ID
    if (urlObj.hostname.includes("youtube.com")) {
      const videoId = urlObj.searchParams.get("v");
      if (videoId) return `https://www.youtube.com/embed/${videoId}`;
    }

    // If it’s already an embed URL or unknown format, return as-is
    return url;
  } catch {
    return url;
  }
};

const VideoBox = ({ url, title = "YouTube Video" }) => {
  const embedUrl = toEmbedUrl(url);

  return (
    <div className={styles.videoContainer}>
      <iframe
        className={styles.videoFrame}
        src={embedUrl}
        title={title}
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      ></iframe>
    </div>
  );
};

export default VideoBox;
