import React from 'react';
import Icon from '../Icon/Icon'

/**
 * LinkIconAtom
 * Displays a provider logo as a clickable link
 * Props:
 *  - provider: { provider_name, logo_url, access_type, link, country }
 *  - size: optional size for the icon (e.g., 32)
 */
const LinkIconAtom = ({ provider, size = 32 }) => {
  if (!provider || !provider.link || !provider.logo_url) return null;

  return (
    <a
      href={provider.link}
      target="_blank"
      rel="noopener noreferrer"
      title={`${provider.provider_name} (${provider.access_type})`}
      style={{ display: 'inline-block', width: size, height: size }}
    >
      <img
        src={provider.logo_url}
        alt={provider.provider_name}
        width={size}
        height={size}
        style={{ objectFit: 'contain', borderRadius: 4 }}
      />
    </a>
  );
};

export default LinkIconAtom;
