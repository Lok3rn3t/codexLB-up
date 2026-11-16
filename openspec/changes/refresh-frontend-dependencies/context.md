# Frontend compatibility

The i18next 27 overloads do not accept an explicit undefined options argument;
the existing wrappers use an empty options object when there is nothing to
interpolate. For example, a translated label with no values still uses the same
translation key and default language.

MSW 3 renamed `onUnhandledRequest` to `onUnhandledFrame`. The mock server keeps
the `error` strategy so an unexpected HTTP request still fails tests instead of
escaping to the network. See the [MSW 3 release notes](https://github.com/mswjs/msw/releases/tag/v3.0.0).

The legend tests verify the rendered color through `backgroundColor`; this
avoids depending on how jsdom serializes the `background` shorthand while
retaining the grey missing-agent and blue normal-palette checks.

The build uses TypeScript 7.0.2 through the `@typescript/native` alias. The
`typescript` package used by typescript-eslint stays on 6.0.3 because current
typescript-eslint 8.72.2 explicitly rejects TypeScript 7.0. This split is an
upstream compatibility constraint, not a skipped compiler upgrade.
