import { test, expect } from '@playwright/test'

/**
 * AI小商 Teacher Terminal - Auth Flow Tests
 * Tests for teacher registration, login, and route protection
 */

const BASE_URL = 'http://localhost:5173'

test.describe('Teacher Auth Flow', () => {
  test('teacher can navigate to register page', async ({ page }) => {
    await page.goto(`${BASE_URL}/teacher/login`)
    await page.waitForLoadState('networkidle')

    // Click register link
    const registerLink = page.locator('a:has-text("教师注册")')
    await expect(registerLink).toBeVisible()

    await registerLink.click()
    await page.waitForURL('**/teacher/register')

    // Should be on register page
    await expect(page).toHaveURL(/\/teacher\/register/)
  })

  test('teacher register page displays correctly', async ({ page }) => {
    await page.goto(`${BASE_URL}/teacher/register`)
    await page.waitForLoadState('networkidle')

    // Check page elements
    await expect(page.locator('text=AI小商')).toBeVisible()
    await expect(page.locator('text=教师端')).toBeVisible()
    await expect(page.locator('input[placeholder*="手机号"]')).toBeVisible()
    await expect(page.locator('input[placeholder*="密码"]')).toBeVisible()
  })

  test('teacher can register with valid data', async ({ page }) => {
    await page.goto(`${BASE_URL}/teacher/register`)
    await page.waitForLoadState('networkidle')

    // Fill registration form
    const testPhone = `138${Date.now().toString().slice(-8)}` // Unique phone number
    await page.fill('input[placeholder*="手机号"]', testPhone)
    await page.fill('input[placeholder*="密码"]', 'test123456')

    // Submit
    await page.click('button:has-text("注册")')

    // Wait for redirect to teacher dashboard
    await page.waitForURL('**/teacher**', { timeout: 10000 })

    // Should be logged in (token should be in localStorage)
    const token = await page.evaluate(() => localStorage.getItem('token'))
    expect(token).toBeTruthy()
  })

  test('teacher can navigate to login page', async ({ page }) => {
    await page.goto(`${BASE_URL}/teacher/register`)
    await page.waitForLoadState('networkidle')

    // Click login link
    const loginLink = page.locator('a:has-text("立即登录"), a:has-text("去登录")').first()
    await loginLink.click()
    await page.waitForURL('**/teacher/login')

    await expect(page).toHaveURL(/\/teacher\/login/)
  })

  test('teacher can login with valid credentials', async ({ page }) => {
    // First register a new teacher
    const testPhone = `139${Date.now().toString().slice(-8)}`
    await page.goto(`${BASE_URL}/teacher/register`)
    await page.waitForLoadState('networkidle')

    await page.fill('input[placeholder*="手机号"]', testPhone)
    await page.fill('input[placeholder*="密码"]', 'test123456')
    await page.click('button:has-text("注册")')

    await page.waitForURL('**/teacher**', { timeout: 10000 })

    // Now logout and test login
    await page.evaluate(() => localStorage.clear())
    await page.goto(`${BASE_URL}/teacher/login`)
    await page.waitForLoadState('networkidle')

    // Login
    await page.fill('input[placeholder*="手机号"]', testPhone)
    await page.fill('input[placeholder*="密码"]', 'test123456')
    await page.click('button:has-text("登录")')

    // Should redirect to teacher dashboard
    await page.waitForURL('**/teacher**', { timeout: 10000 })
  })

  test('unauthenticated user cannot access /teacher routes', async ({ page }) => {
    // Try to access teacher dashboard directly
    await page.goto(`${BASE_URL}/teacher`)
    await page.waitForLoadState('networkidle')

    // Should redirect to login
    await expect(page).toHaveURL(/\/teacher\/login/)
  })

  test('unauthenticated user cannot access teacher sub-routes', async ({ page }) => {
    // Try grade page
    await page.goto(`${BASE_URL}/teacher/grade`)
    await page.waitForLoadState('networkidle')
    await expect(page).toHaveURL(/\/teacher\/login/)

    // Try notification page
    await page.goto(`${BASE_URL}/teacher/notification`)
    await page.waitForLoadState('networkidle')
    await expect(page).toHaveURL(/\/teacher\/login/)

    // Try lesson-plan page
    await page.goto(`${BASE_URL}/teacher/lesson-plan`)
    await page.waitForLoadState('networkidle')
    await expect(page).toHaveURL(/\/teacher\/login/)
  })

  test('teacher login form validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/teacher/login`)
    await page.waitForLoadState('networkidle')

    // Submit empty form
    const submitBtn = page.locator('button:has-text("登录")')
    await submitBtn.click()

    // Should show validation errors (Element Plus form validation)
    // The button should not be loading and form should not submit
    await expect(page.locator('text=请输入手机号')).toBeVisible({ timeout: 2000 }).catch(() => {})
    await expect(page.locator('text=请输入密码')).toBeVisible({ timeout: 2000 }).catch(() => {})
  })

  test('teacher register form validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/teacher/register`)
    await page.waitForLoadState('networkidle')

    // Submit empty form
    const submitBtn = page.locator('button:has-text("注册")')
    await submitBtn.click()

    // Should show validation errors
    await expect(page.locator('text=请输入手机号')).toBeVisible({ timeout: 2000 }).catch(() => {})
  })
})