import React from 'react';
import styles from './UserProfile.module.css';
import MovieTitleContainer from "../../molecules/MovieTitleContainer/MovieTitleContainer";
import MovieMeta from "../../molecules/MovieMeta/MovieMeta";
import PosterImage from "../../atoms/PosterImage/PosterImage";

function UserProfile({ username, profilepicture, rank, reviews_written, movies_watched, movies_added }) {
  return (
    <div className={styles.container}>
      <div className={styles.leftColumn}>
        <MovieTitleContainer
          title={username}
          synopsis={`Rank: ${rank}`}
        />
      </div>

      <div className={styles.rightColumn}>
        <PosterImage
          src={profilepicture}
          alt={`${username}'s profile picture`}
        />

        <MovieMeta
          director={`Reviews Written: ${reviews_written}`}
          releaseDate={`Movies Watched: ${movies_watched}`}
        />

        <MovieMeta
          director={`Movies Added: ${movies_added}`}
          releaseDate={``}
        />
      </div>
    </div>
  );
}

export default UserProfile;
