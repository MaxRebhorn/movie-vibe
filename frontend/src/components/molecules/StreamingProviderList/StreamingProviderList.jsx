// StreamingProviderList.jsx
import styles from "./StreamingProviderList.module.css";
import LinkIcon from "../../atoms/LinkIcon/LinkIcon"; // adjust path
import '../../../styles/colors.css';

export default function StreamingProviderList({ providers }) {
  // Ensure providers is at least an empty array
  const safeProviders = providers || [];

  if (safeProviders.length === 0) return null;

  return (
    <div className={styles.castList} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
      {safeProviders.map((provider) => (
        <LinkIcon
          key={provider.provider_name + provider.country}
          provider={provider}
          size={40}
        />
      ))}
    </div>
  );
}
