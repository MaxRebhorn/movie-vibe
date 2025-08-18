import { NavItem } from '../molecules/NavItem';
import { Button } from '../atoms/Button';
import { Icon } from '../atoms/Icon';

export const Navigation = () => {
  return (
    <div className="navigation-2">
      <div className="items-3">
        <NavItem label="Page" />
        <NavItem label="Page" />
        <NavItem label="Page" />
        <Button>Button</Button>
      </div>
      <div className="image2vector-1-9">
        <Icon src="/images/path0-11.svg" />
        <Icon src="/images/path1-12.svg" />
        <Icon src="/images/path2-13.svg" />
        <Icon src="/images/path3-14.svg" />
        <Icon src="/images/path4-15.svg" />
      </div>
    </div>
  );
};
