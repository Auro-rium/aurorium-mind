# Aurorium Mind design system

## Product

An evidence-oriented personal reasoning assistant. The interface should feel
like an intelligent instrument: calm, considered, direct, and built for long
thinking sessions—not a generic chatbot or a sci-fi gimmick.

## Visual direction

- Near-black ink background with warm graphite surfaces.
- Acid-lime signal color used sparingly for live/ready states and primary action.
- Off-white typography, muted stone secondary text, subtle hairline borders.
- Clean neo-grotesk sans typography; no gradient blobs, glassmorphism, or neon
  cyberpunk effects.
- Generous desktop whitespace, dense but readable chat content, mobile-first
  composer behavior.

## Tokens

- Background: `#0A0B0A`; surface: `#111310`; elevated: `#181B17`.
- Text: `#F1F2EA`; muted: `#9CA095`; border: `#2A2E28`.
- Accent: `#C8FF3D`; accent ink: `#142000`; danger: `#FF6B5F`.
- Radius: 14px cards, 20px composer, 999px status chips.
- Shadows: soft black `0 18px 60px rgba(0,0,0,.28)` only.
- Motion: 160–220ms ease-out; respect reduced motion.

## Chat page

Use a restrained two-column desktop workspace: a narrow contextual rail and a
large conversation canvas. On mobile, collapse the rail into a compact top
status strip. Make the empty state useful with three starter thinking prompts.
The composer is anchored at the bottom and must visibly communicate keyboard
submission and backend status.
