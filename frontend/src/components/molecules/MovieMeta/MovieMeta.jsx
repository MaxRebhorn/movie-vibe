import styles from "./MovieMeta.module.css";
import MetaText from "../../atoms/MetaText/MetaText";

export default function MovieMeta({
  director,
  releaseDate,
  streaming_providers = [] // destructure the API response directly
}) {
  return (
    <div className={styles.metaContainer}>
      <MetaText label="Director" value={director} />
      <MetaText label="Release Date" value={releaseDate} />

      {streaming_providers.length > 0 && (
        <div className={styles.providersContainer}>
          <h4 className={styles.providersTitle}>Available On</h4>
          <div className={styles.providersGrid}>
            {streaming_providers.map((provider) => (
              <a
                key={`${provider.id}-${provider.access_type}`}
                href={provider.link}
                target="_blank"
                rel="noopener noreferrer"
                className={`${styles.providerCard} ${styles[provider.access_type]}`}
              >
                {provider.logo_url && (
                  <img
                    src={provider.logo_url}
                    alt={provider.name}
                    className={styles.providerLogo}
                  />
                )}
                <span className={styles.providerName}>{provider.name}</span>
                <span className={styles.providerType}>
                  {provider.access_type.charAt(0).toUpperCase() + provider.access_type.slice(1)}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

