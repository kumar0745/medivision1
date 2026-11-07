import { test, expect } from '@playwright/test';

test('visitor can explore the demo and navigate wellness sections', async ({ page }) => {
  await page.route('**/api/auth/me', route => route.fulfill({
    status: 401, contentType: 'application/json',
    body: JSON.stringify({ detail: 'Please sign in again.' }),
  }));
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Health, made clearer/i })).toBeVisible();
  await page.getByRole('button', { name: /Explore interactive demo/i }).click();
  await expect(page.getByText('Sample demo profile')).toBeVisible();
  await page.getByRole('button', { name: 'Wellness', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'How are you feeling today?' })).toBeVisible();
  await page.getByRole('button', { name: 'Profile', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Your profile' })).toBeVisible();
});

test('sign-in establishes a session and opens the dashboard', async ({ page }) => {
  await page.route('**/api/health', route => route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify({security: {password_reset_email: 'configured', malware_scanning: 'configured'}})}));
  const user = {
    id: 77, full_name: 'Pavan Test', email: 'pavan@example.test',
    age: 24, age_group: '16-30', health_goal: 'fitness',
    women_health_opt_in: false,
  };
  await page.route('**/api/auth/me', route => route.fulfill({
    status: 401, contentType: 'application/json',
    body: JSON.stringify({ detail: 'Please sign in again.' }),
  }));
  await page.route('**/api/auth/login', route => route.fulfill({
    status: 200, contentType: 'application/json',
    body: JSON.stringify({ token_type: 'cookie', user }),
  }));
  await page.route('**/api/dashboard', route => route.fulfill({
    status: 200, contentType: 'application/json',
    body: JSON.stringify({
      user: { full_name: user.full_name, age_group: user.age_group, health_goal: user.health_goal },
      wellness_count: 0, diagnosis_count: 0, latest_wellness: null,
      recent_records: [], cycle_tracking_enabled: false, cycle_count: 0,
    }),
  }));

  await page.goto('/');
  await page.getByLabel('Email address').fill(user.email);
  await page.getByLabel('Password').fill('StrongTestPassword!234');
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Good morning, Pavan.' })).toBeVisible();
  await expect(page.getByText('Your account data')).toBeVisible();
});

test('forgot password gives the same non-enumerating confirmation', async ({ page }) => {
  await page.route('**/api/health', route => route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify({security: {password_reset_email: 'configured', malware_scanning: 'configured'}})}));
  await page.route('**/api/auth/me', route => route.fulfill({
    status: 401, contentType: 'application/json',
    body: JSON.stringify({ detail: 'Please sign in again.' }),
  }));
  await page.route('**/api/auth/forgot-password', route => route.fulfill({
    status: 202, contentType: 'application/json',
    body: JSON.stringify({ message: 'If an account exists for that email, a password-reset link will be sent.' }),
  }));
  await page.goto('/');
  await page.getByRole('button', { name: 'Forgot password?' }).click();
  await expect(page.getByRole('heading', { name: 'Reset your password' })).toBeVisible();
  await page.getByLabel('Email address').fill('unknown@example.test');
  await page.getByRole('button', { name: 'Send reset link' }).click();
  await expect(page.getByText('If an account exists for that email, a password-reset link will be sent.')).toBeVisible();
});

test('reset link changes the password and returns to sign-in', async ({ page }) => {
  await page.route('**/api/auth/me', route => route.fulfill({
    status: 401, contentType: 'application/json',
    body: JSON.stringify({ detail: 'Please sign in again.' }),
  }));
  let requestBody;
  await page.route('**/api/auth/reset-password', async route => {
    requestBody = route.request().postDataJSON();
    await route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({ message: 'Password updated. Sign in with your new password.' }),
    });
  });
  await page.goto('/#reset_token=synthetic-playwright-reset-token');
  await expect(page.getByRole('heading', { name: 'Choose a new password' })).toBeVisible();
  await page.getByLabel('New password').fill('NewStrongTestPassword!456');
  await page.getByRole('button', { name: 'Update password' }).click();
  await expect(page.getByRole('heading', { name: 'Sign in to MediVision' })).toBeVisible();
  expect(requestBody.token).toBe('synthetic-playwright-reset-token');
  expect(requestBody.password).toBe('NewStrongTestPassword!456');
});

test('new visitor can register with explicit privacy consent', async ({ page }) => {
  await page.route('**/api/health', route => route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify({security: {password_reset_email: 'configured', malware_scanning: 'configured'}})}));
  const user = {
    id: 88, full_name: 'Asha Test', email: 'asha@example.test',
    age: 22, age_group: '16-30', health_goal: 'prevent',
    women_health_opt_in: false,
  };
  await page.route('**/api/auth/me', route => route.fulfill({
    status: 401, contentType: 'application/json',
    body: JSON.stringify({ detail: 'Please sign in again.' }),
  }));
  await page.route('**/api/auth/register', route => route.fulfill({
    status: 200, contentType: 'application/json',
    body: JSON.stringify({ token_type: 'cookie', user }),
  }));
  await page.route('**/api/dashboard', route => route.fulfill({
    status: 200, contentType: 'application/json',
    body: JSON.stringify({
      user: { full_name: user.full_name, age_group: user.age_group, health_goal: user.health_goal },
      wellness_count: 0, diagnosis_count: 0, latest_wellness: null,
      recent_records: [], cycle_tracking_enabled: false, cycle_count: 0,
    }),
  }));
  await page.goto('/');
  await page.getByRole('button', { name: 'Create account', exact: true }).click();
  await page.getByLabel('Full name').fill(user.full_name);
  await page.getByLabel('Email address').fill(user.email);
  await page.getByLabel('Password').fill('StrongTestPassword!234');
  await page.getByText('I consent to saving my account and wellness entries').click();
  await page.getByRole('button', { name: 'Create account', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Good morning, Asha.' })).toBeVisible();
});


test('signed-in users see that attachments are disabled until scanning is active', async ({ page }) => {
  const user = {id: 99, full_name: 'Asha Test', email: 'asha@example.test', age: 22, age_group: '16-30', health_goal: 'prevent', women_health_opt_in: false};
  await page.route('**/api/health', route => route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify({security: {password_reset_email: 'not_configured', malware_scanning: 'disabled_fail_closed'}})}));
  await page.route('**/api/auth/me', route => route.fulfill({status: 401, contentType: 'application/json', body: JSON.stringify({detail: 'Please sign in again.'})}));
  await page.route('**/api/auth/login', route => route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify({token_type: 'cookie', user})}));
  await page.route('**/api/dashboard', route => route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify({user: {full_name: user.full_name, age_group: user.age_group, health_goal: user.health_goal}, wellness_count: 0, diagnosis_count: 0, latest_wellness: null, recent_records: [], cycle_tracking_enabled: false, cycle_count: 0})}));
  await page.route('**/api/diagnosis', route => route.fulfill({status: 200, contentType: 'application/json', body: '[]'}));
  await page.goto('/');
  await page.getByLabel('Email address').fill(user.email);
  await page.getByLabel('Password').fill('StrongTestPassword!234');
  await page.getByRole('button', {name: 'Sign in', exact: true}).click();
  await page.getByRole('button', {name: 'Health check', exact: true}).click();
  await expect(page.getByText('Secure file scanning is not active yet')).toBeVisible();
  await expect(page.locator('input[type=file]')).toBeDisabled();
});
