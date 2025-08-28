import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  await page.getByRole('link').nth(4).click();
  await page.getByRole('link', { name: 'Sign up' }).click();
  await page.getByRole('textbox', { name: 'Username*' }).click();
  await page.getByRole('textbox', { name: 'Username*' }).fill('Jeff111');
  await page.getByRole('textbox', { name: 'Username*' }).press('Tab');
  await page.getByRole('textbox', { name: 'Email*' }).fill('jeff');
  await page.getByRole('textbox', { name: 'Email*' }).press('Alt+ControlOrMeta+q');
  await page.getByRole('textbox', { name: 'Email*' }).fill('jeff@jeff.com');
  await page.getByRole('textbox', { name: 'Email*' }).press('Tab');
  await page.getByRole('textbox', { name: 'First Name' }).fill('Jeff');
  await page.getByRole('textbox', { name: 'First Name' }).press('Tab');
  await page.getByRole('textbox', { name: 'Last Name' }).fill('Jeff');
  await page.getByRole('textbox', { name: 'Last Name' }).press('Tab');
  await page.getByRole('textbox', { name: 'Password*', exact: true }).fill('Jeff1234567');
  await page.getByRole('textbox', { name: 'Confirm Password*' }).click();
  await page.getByRole('textbox', { name: 'Confirm Password*' }).fill('Jeff1234567');
  await page.getByRole('button', { name: 'Create Account' }).click();
  await page.getByRole('textbox', { name: 'Username*' }).click();
  await page.getByRole('textbox', { name: 'Username*' }).fill('Jeff111');
  await page.getByRole('textbox', { name: 'Password*' }).click();
  await page.getByRole('textbox', { name: 'Password*' }).fill('Jeff1234567');
  await page.getByRole('button', { name: 'Sign In' }).click();
});