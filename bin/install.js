#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');
const crypto = require('crypto');

// Colors (using 256-color mode for better terminal compatibility)
const cyan = '\x1b[38;5;37m'; // Closest to #2FA7A0 in 256-color palette
const green = '\x1b[32m';
const yellow = '\x1b[33m';
const dim = '\x1b[2m';
const reset = '\x1b[0m';

// Get version from package.json
const pkg = require('../package.json');

const banner = `
${cyan}   ███╗   ███╗██╗███╗   ██╗██████╗ ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
   ████╗ ████║██║████╗  ██║██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
   ██╔████╔██║██║██╔██╗ ██║██║  ██║███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
   ██║╚██╔╝██║██║██║╚██╗██║██║  ██║╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
   ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
   ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝${reset}

  Mindsystem ${dim}v${pkg.version}${reset}
  A meta-prompting, context engineering and spec-driven
  development system for Claude Code by Roland Tolnay.
  Based on GSD by TÂCHES.
`;

// Parse args
const args = process.argv.slice(2);
const hasGlobal = args.includes('--global') || args.includes('-g');
const hasLocal = args.includes('--local') || args.includes('-l');

// Parse --config-dir argument
function parseConfigDirArg() {
  const configDirIndex = args.findIndex(arg => arg === '--config-dir' || arg === '-c');
  if (configDirIndex !== -1) {
    const nextArg = args[configDirIndex + 1];
    // Error if --config-dir is provided without a value or next arg is another flag
    if (!nextArg || nextArg.startsWith('-')) {
      console.error(`  ${yellow}--config-dir requires a path argument${reset}`);
      process.exit(1);
    }
    return nextArg;
  }
  // Also handle --config-dir=value format
  const configDirArg = args.find(arg => arg.startsWith('--config-dir=') || arg.startsWith('-c='));
  if (configDirArg) {
    return configDirArg.split('=')[1];
  }
  return null;
}
const explicitConfigDir = parseConfigDirArg();
const hasForce = args.includes('--force') || args.includes('-f');
const hasHelp = args.includes('--help') || args.includes('-h');

console.log(banner);

// Show help if requested
if (hasHelp) {
  console.log(`  ${yellow}Usage:${reset} npx mindsystem-cc [options]

  ${yellow}Options:${reset}
    ${cyan}-g, --global${reset}              Install globally (to Claude config directory)
    ${cyan}-l, --local${reset}               Install locally (to ./.claude in current directory)
    ${cyan}-c, --config-dir <path>${reset}   Specify custom Claude config directory
    ${cyan}-f, --force${reset}               Overwrite modified files without prompting
    ${cyan}-h, --help${reset}                Show this help message

  ${yellow}Examples:${reset}
    ${dim}# Install to default ~/.claude directory${reset}
    npx mindsystem-cc --global

    ${dim}# Install to custom config directory (for multiple Claude accounts)${reset}
    npx mindsystem-cc --global --config-dir ~/.claude-bc

    ${dim}# Using environment variable${reset}
    CLAUDE_CONFIG_DIR=~/.claude-bc npx mindsystem-cc --global

    ${dim}# Install to current project only${reset}
    npx mindsystem-cc --local

  ${yellow}Notes:${reset}
    The --config-dir option is useful when you have multiple Claude Code
    configurations (e.g., for different subscriptions). It takes priority
    over the CLAUDE_CONFIG_DIR environment variable.
`);
  process.exit(0);
}

/**
 * Expand ~ to home directory (shell doesn't expand in env vars passed to node)
 */
function expandTilde(filePath) {
  if (filePath && filePath.startsWith('~/')) {
    return path.join(os.homedir(), filePath.slice(2));
  }
  return filePath;
}

/**
 * Compute SHA-256 checksum truncated to 16 chars
 */
function computeChecksum(content) {
  return crypto.createHash('sha256').update(content).digest('hex').slice(0, 16);
}

/**
 * Read and parse manifest file, return null if missing/corrupted
 */
function readManifest(claudeDir) {
  const manifestPath = path.join(claudeDir, 'mindsystem', '.manifest.json');
  try {
    if (!fs.existsSync(manifestPath)) {
      return null;
    }
    const content = fs.readFileSync(manifestPath, 'utf8');
    return JSON.parse(content);
  } catch (e) {
    console.log(`  ${yellow}⚠${reset} Manifest corrupted, treating as fresh install`);
    return null;
  }
}

/**
 * Write manifest JSON file
 */
function writeManifest(claudeDir, manifest) {
  const manifestDir = path.join(claudeDir, 'mindsystem');
  fs.mkdirSync(manifestDir, { recursive: true });
  const manifestPath = path.join(manifestDir, '.manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
}

/**
 * Check if running in interactive TTY
 */
function isInteractive() {
  return process.stdin.isTTY && process.stdout.isTTY;
}

/**
 * Recursively collect files with relative paths
 * @param {string} baseDir - The base directory for relative path calculation
 * @param {string} currentDir - The current directory being scanned
 * @param {string} destPrefix - The destination prefix (e.g., 'commands/ms', 'agents')
 * @returns {Array<{relativePath: string, absolutePath: string}>}
 */
// Directories and file patterns excluded from installation
const EXCLUDED_DIRS = new Set(['.pytest_cache', '__pycache__', 'fixtures', 'node_modules', '.git', '.venv']);
const EXCLUDED_FILE_PATTERNS = [/^test_/, /\.test\./, /\.spec\./];

function collectFiles(baseDir, currentDir, destPrefix) {
  const files = [];
  if (!fs.existsSync(currentDir)) {
    return files;
  }

  const entries = fs.readdirSync(currentDir, { withFileTypes: true });
  for (const entry of entries) {
    if (EXCLUDED_DIRS.has(entry.name)) {
      continue;
    }

    const absolutePath = path.join(currentDir, entry.name);
    const relativeToCurrent = path.relative(baseDir, absolutePath);
    const relativePath = path.join(destPrefix, relativeToCurrent);

    if (entry.isDirectory()) {
      files.push(...collectFiles(baseDir, absolutePath, destPrefix));
    } else if (!EXCLUDED_FILE_PATTERNS.some(p => p.test(entry.name))) {
      files.push({ relativePath, absolutePath });
    }
  }
  return files;
}

/**
 * Build complete list of files to install from all source directories
 * @param {string} src - The source directory (mindsystem package root)
 * @returns {Array<{relativePath: string, absolutePath: string}>}
 */
function buildInstallManifest(src) {
  const files = [];

  // commands/ms
  const commandsSrc = path.join(src, 'commands', 'ms');
  files.push(...collectFiles(commandsSrc, commandsSrc, 'commands/ms'));

  // mindsystem
  const mindsystemSrc = path.join(src, 'mindsystem');
  files.push(...collectFiles(mindsystemSrc, mindsystemSrc, 'mindsystem'));

  // agents
  const agentsSrc = path.join(src, 'agents');
  files.push(...collectFiles(agentsSrc, agentsSrc, 'agents'));

  // scripts -> mindsystem/scripts
  const scriptsSrc = path.join(src, 'scripts');
  files.push(...collectFiles(scriptsSrc, scriptsSrc, 'mindsystem/scripts'));

  // skills
  const skillsSrc = path.join(src, 'skills');
  files.push(...collectFiles(skillsSrc, skillsSrc, 'skills'));

  // CHANGELOG.md -> mindsystem/CHANGELOG.md
  const changelogSrc = path.join(src, 'CHANGELOG.md');
  if (fs.existsSync(changelogSrc)) {
    files.push({ relativePath: 'mindsystem/CHANGELOG.md', absolutePath: changelogSrc });
  }

  return files;
}

/**
 * Compare manifests to detect orphans and conflicts
 * @param {Object|null} oldManifest - Previous manifest or null for fresh install
 * @param {string} claudeDir - Target directory
 * @param {Array} newFiles - Files to install
 * @param {string} pathPrefix - Path prefix for content replacement
 * @returns {{orphans: string[], conflicts: Array<{relativePath: string, reason: string}>}}
 */
function compareManifests(oldManifest, claudeDir, newFiles, pathPrefix) {
  const orphans = [];
  const conflicts = [];

  // Build set of new file paths
  const newFilePaths = new Set(newFiles.map(f => f.relativePath));

  // Find orphans (files in old manifest but not in new)
  if (oldManifest && oldManifest.files) {
    for (const oldPath of Object.keys(oldManifest.files)) {
      if (!newFilePaths.has(oldPath)) {
        const fullPath = path.join(claudeDir, oldPath);
        if (fs.existsSync(fullPath)) {
          orphans.push(oldPath);
        }
      }
    }
  }

  // Find conflicts (installed files modified by user)
  if (oldManifest && oldManifest.files) {
    for (const fileInfo of newFiles) {
      const destPath = path.join(claudeDir, fileInfo.relativePath);
      if (!fs.existsSync(destPath)) {
        continue; // New file, no conflict
      }

      const oldChecksum = oldManifest.files[fileInfo.relativePath];
      if (!oldChecksum) {
        continue; // File not in old manifest, treat as new
      }

      // Read current installed content
      const installedContent = fs.readFileSync(destPath, 'utf8');
      const installedChecksum = computeChecksum(installedContent);

      // If installed file differs from what we last installed, it's been modified
      if (installedChecksum !== oldChecksum) {
        // Read source content with path replacement to compare
        let sourceContent = fs.readFileSync(fileInfo.absolutePath, 'utf8');
        if (fileInfo.absolutePath.endsWith('.md')) {
          sourceContent = sourceContent.replace(/~\/\.claude\//g, pathPrefix);
        }
        const sourceChecksum = computeChecksum(sourceContent);

        // Only conflict if source is also different (user modified AND we have changes)
        if (sourceChecksum !== installedChecksum) {
          conflicts.push({
            relativePath: fileInfo.relativePath,
            reason: 'locally modified'
          });
        }
      }
    }
  }

  return { orphans, conflicts };
}

/**
 * Interactive conflict resolution
 * @param {Array} conflicts - List of conflicting files
 * @param {boolean} forceOverwrite - Skip prompts and overwrite all
 * @returns {Promise<{overwrite: Set<string>, keep: Set<string>}>}
 */
async function resolveConflicts(conflicts, forceOverwrite) {
  const overwrite = new Set();
  const keep = new Set();

  if (conflicts.length === 0) {
    return { overwrite, keep };
  }

  if (forceOverwrite) {
    for (const c of conflicts) {
      overwrite.add(c.relativePath);
    }
    console.log(`  ${yellow}⚠${reset} Force overwriting ${conflicts.length} modified file(s)`);
    return { overwrite, keep };
  }

  if (!isInteractive()) {
    for (const c of conflicts) {
      overwrite.add(c.relativePath);
    }
    console.log(`  ${yellow}⚠${reset} Non-interactive mode: overwriting ${conflicts.length} modified file(s)`);
    return { overwrite, keep };
  }

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));

  console.log(`\n  ${yellow}${conflicts.length} file(s) have local modifications:${reset}\n`);

  let overwriteAll = false;
  let keepAll = false;

  for (const conflict of conflicts) {
    if (overwriteAll) {
      overwrite.add(conflict.relativePath);
      continue;
    }
    if (keepAll) {
      keep.add(conflict.relativePath);
      continue;
    }

    console.log(`  ${dim}${conflict.relativePath}${reset}`);
    const answer = await question(`  [O]verwrite, [K]eep, [A]ll overwrite, [N]one keep? `);

    switch (answer.toLowerCase().trim()) {
      case 'o':
      case 'overwrite':
        overwrite.add(conflict.relativePath);
        break;
      case 'k':
      case 'keep':
        keep.add(conflict.relativePath);
        break;
      case 'a':
      case 'all':
        overwriteAll = true;
        overwrite.add(conflict.relativePath);
        break;
      case 'n':
      case 'none':
        keepAll = true;
        keep.add(conflict.relativePath);
        break;
      default:
        // Default to overwrite
        overwrite.add(conflict.relativePath);
    }
  }

  rl.close();
  console.log('');
  return { overwrite, keep };
}

/**
 * Remove orphaned files and empty directories
 * @param {string} claudeDir - Target directory
 * @param {string[]} filesToRemove - Relative paths of files to remove
 */
function cleanupOrphanedFiles(claudeDir, filesToRemove) {
  if (filesToRemove.length === 0) {
    return;
  }

  const dirsToCheck = new Set();

  for (const relativePath of filesToRemove) {
    const fullPath = path.join(claudeDir, relativePath);
    try {
      if (fs.existsSync(fullPath)) {
        fs.unlinkSync(fullPath);
        console.log(`  ${yellow}✗${reset} Removed ${relativePath}`);
        // Track parent directories for cleanup
        dirsToCheck.add(path.dirname(fullPath));
      }
    } catch (e) {
      console.log(`  ${yellow}⚠${reset} Failed to remove ${relativePath}: ${e.message}`);
    }
  }

  // Remove empty directories (deepest first)
  const sortedDirs = Array.from(dirsToCheck).sort((a, b) => b.length - a.length);
  for (const dir of sortedDirs) {
    try {
      // Don't remove the claudeDir itself or its immediate children (commands, agents, etc.)
      if (dir === claudeDir || path.dirname(dir) === claudeDir) {
        continue;
      }
      const entries = fs.readdirSync(dir);
      if (entries.length === 0) {
        fs.rmdirSync(dir);
      }
    } catch (e) {
      // Ignore errors (directory not empty or doesn't exist)
    }
  }
}

/**
 * Generate CLI wrapper scripts and configure PATH hook
 */
function generateWrappers(claudeDir) {
  const binDir = path.join(claudeDir, 'bin');
  fs.mkdirSync(binDir, { recursive: true });

  const wrappers = {
    'ms-tools': '#!/usr/bin/env bash\nexec uv run "$(dirname "$0")/../mindsystem/scripts/ms-tools.py" "$@"\n',
    'ms-lookup': '#!/usr/bin/env bash\nexec "$(dirname "$0")/../mindsystem/scripts/ms-lookup-wrapper.sh" "$@"\n',
    'ms-compare-mockups': '#!/usr/bin/env bash\nexec uv run "$(dirname "$0")/../mindsystem/scripts/compare_mockups.py" "$@"\n',
  };

  for (const [name, content] of Object.entries(wrappers)) {
    fs.writeFileSync(path.join(binDir, name), content);
    fs.chmodSync(path.join(binDir, name), '755');
  }

  console.log(`  ${green}✓${reset} Generated CLI wrappers (${Object.keys(wrappers).join(', ')})`);
}

function ensurePathHook(claudeDir, isGlobal, configDir) {
  const settingsPath = path.join(claudeDir, 'settings.json');
  let settings = {};
  if (fs.existsSync(settingsPath)) {
    settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  }

  if (!settings.hooks) settings.hooks = {};
  if (!Array.isArray(settings.hooks.SessionStart))
    settings.hooks.SessionStart = [];

  // Idempotent — skip if already present
  const marker = 'mindsystem/bin';
  if (settings.hooks.SessionStart.some(e => JSON.stringify(e).includes(marker)))
    return;

  // Build PATH expression
  let binExpr;
  if (isGlobal) {
    binExpr = configDir
      ? `${claudeDir}/bin`
      : '$HOME/.claude/bin';
  } else {
    binExpr = '$CLAUDE_PROJECT_DIR/.claude/bin';
  }

  settings.hooks.SessionStart.push({
    matcher: '',
    hooks: [{
      type: 'command',
      command: `echo 'export PATH="${binExpr}:$PATH"' >> "$CLAUDE_ENV_FILE"`
    }]
  });

  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
  console.log(`  ${green}✓${reset} Configured PATH hook`);
}

/**
 * Recursively copy directory, replacing paths in .md files
 */
function copyWithPathReplacement(srcDir, destDir, pathPrefix) {
  fs.mkdirSync(destDir, { recursive: true });

  const entries = fs.readdirSync(srcDir, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(srcDir, entry.name);
    const destPath = path.join(destDir, entry.name);

    if (entry.isDirectory()) {
      copyWithPathReplacement(srcPath, destPath, pathPrefix);
    } else if (entry.name.endsWith('.md')) {
      // Replace ~/.claude/ with the appropriate prefix in markdown files
      let content = fs.readFileSync(srcPath, 'utf8');
      content = content.replace(/~\/\.claude\//g, pathPrefix);
      fs.writeFileSync(destPath, content);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

/**
 * Recursively copy directory without path replacement
 */
function copyDir(srcDir, destDir) {
  fs.mkdirSync(destDir, { recursive: true });

  const entries = fs.readdirSync(srcDir, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(srcDir, entry.name);
    const destPath = path.join(destDir, entry.name);

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

/**
 * Install a single file with path replacement
 * @param {string} srcPath - Source file path
 * @param {string} destPath - Destination file path
 * @param {string} pathPrefix - Path prefix for .md file replacement
 */
function installFile(srcPath, destPath, pathPrefix) {
  fs.mkdirSync(path.dirname(destPath), { recursive: true });

  if (srcPath.endsWith('.md')) {
    let content = fs.readFileSync(srcPath, 'utf8');
    content = content.replace(/~\/\.claude\//g, pathPrefix);
    fs.writeFileSync(destPath, content);
  } else {
    fs.copyFileSync(srcPath, destPath);
  }

  // Make scripts executable
  if (srcPath.endsWith('.sh') || srcPath.endsWith('.py')) {
    fs.chmodSync(destPath, '755');
  }
}

/**
 * Install to the specified directory
 */
async function install(isGlobal) {
  const src = path.join(__dirname, '..');
  // Priority: explicit --config-dir arg > CLAUDE_CONFIG_DIR env var > default ~/.claude
  const configDir = expandTilde(explicitConfigDir) || expandTilde(process.env.CLAUDE_CONFIG_DIR);
  const defaultGlobalDir = configDir || path.join(os.homedir(), '.claude');
  const claudeDir = isGlobal
    ? defaultGlobalDir
    : path.join(process.cwd(), '.claude');

  const locationLabel = isGlobal
    ? claudeDir.replace(os.homedir(), '~')
    : claudeDir.replace(process.cwd(), '.');

  // Path prefix for file references
  // Use actual path when CLAUDE_CONFIG_DIR is set, otherwise use ~ shorthand
  const pathPrefix = isGlobal
    ? (configDir ? `${claudeDir}/` : '~/.claude/')
    : './.claude/';

  console.log(`  Installing to ${cyan}${locationLabel}${reset}\n`);

  // Phase 1: Read old manifest
  const oldManifest = readManifest(claudeDir);

  // Phase 2: Build list of files to install
  const filesToInstall = buildInstallManifest(src);

  // Phase 3: Compare and detect conflicts
  const { orphans, conflicts } = compareManifests(oldManifest, claudeDir, filesToInstall, pathPrefix);

  // Phase 4: Resolve conflicts interactively
  const { overwrite, keep } = await resolveConflicts(conflicts, hasForce);

  // Phase 5: Install files (skipping kept files)
  const newManifestFiles = {};
  const categories = {
    'commands/ms': { count: 0, label: 'commands/ms' },
    'mindsystem': { count: 0, label: 'mindsystem' },
    'agents': { count: 0, label: 'agents' },
    'mindsystem/scripts': { count: 0, label: 'scripts' },
    'skills': { count: 0, label: 'skills' }
  };

  for (const fileInfo of filesToInstall) {
    const destPath = path.join(claudeDir, fileInfo.relativePath);

    // Skip files user wants to keep
    if (keep.has(fileInfo.relativePath)) {
      // Still need to track in manifest with current checksum
      const installedContent = fs.readFileSync(destPath, 'utf8');
      newManifestFiles[fileInfo.relativePath] = computeChecksum(installedContent);
      continue;
    }

    // Install the file
    installFile(fileInfo.absolutePath, destPath, pathPrefix);

    // Compute checksum of installed content (after path replacement)
    let installedContent;
    if (fileInfo.absolutePath.endsWith('.md')) {
      installedContent = fs.readFileSync(fileInfo.absolutePath, 'utf8');
      installedContent = installedContent.replace(/~\/\.claude\//g, pathPrefix);
    } else {
      installedContent = fs.readFileSync(destPath, 'utf8');
    }
    newManifestFiles[fileInfo.relativePath] = computeChecksum(installedContent);

    // Track category counts
    for (const prefix of Object.keys(categories)) {
      if (fileInfo.relativePath.startsWith(prefix)) {
        categories[prefix].count++;
        break;
      }
    }
  }

  // Print install summaries
  for (const [prefix, info] of Object.entries(categories)) {
    if (info.count > 0) {
      console.log(`  ${green}✓${reset} Installed ${info.label}`);
    }
  }

  // Phase 6: Write VERSION file
  const versionDest = path.join(claudeDir, 'mindsystem', 'VERSION');
  fs.writeFileSync(versionDest, pkg.version);
  console.log(`  ${green}✓${reset} Wrote VERSION (${pkg.version})`);

  // Phase 7: Generate CLI wrappers and PATH hook
  generateWrappers(claudeDir);
  ensurePathHook(claudeDir, isGlobal, configDir);

  // Phase 8: Check Python for ms-lookup
  const msLookupPath = path.join(claudeDir, 'mindsystem', 'scripts', 'ms-lookup');
  if (fs.existsSync(msLookupPath)) {
    try {
      const { execSync } = require('child_process');
      const pyVersion = execSync('python3 --version 2>&1', { encoding: 'utf8' });
      const versionMatch = pyVersion.match(/(\d+)\.(\d+)/);
      if (versionMatch) {
        const [, major, minor] = versionMatch;
        if (parseInt(major) < 3 || (parseInt(major) === 3 && parseInt(minor) < 9)) {
          console.log(`  ${yellow}⚠${reset} Python 3.9+ required for ms-lookup (found ${major}.${minor})`);
        } else {
          console.log(`  ${green}✓${reset} Installed ms-lookup CLI (Python ${major}.${minor})`);
        }
      }
    } catch (e) {
      console.log(`  ${yellow}⚠${reset} Python not found - ms-lookup CLI requires Python 3.9+`);
    }
  }

  // Phase 9: Cleanup orphaned files
  if (orphans.length > 0) {
    console.log('');
    cleanupOrphanedFiles(claudeDir, orphans);
  }

  // Phase 10: Write new manifest
  const newManifest = {
    version: pkg.version,
    installedAt: new Date().toISOString(),
    files: newManifestFiles
  };
  writeManifest(claudeDir, newManifest);

  console.log(`
  ${green}Done!${reset} Launch Claude Code and run ${cyan}/ms:help${reset}.
`);
}

/**
 * Prompt for install location
 */
async function promptLocation() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const configDir = expandTilde(explicitConfigDir) || expandTilde(process.env.CLAUDE_CONFIG_DIR);
  const globalPath = configDir || path.join(os.homedir(), '.claude');
  const globalLabel = globalPath.replace(os.homedir(), '~');

  console.log(`  ${yellow}Where would you like to install?${reset}

  ${cyan}1${reset}) Global ${dim}(${globalLabel})${reset} - available in all projects
  ${cyan}2${reset}) Local  ${dim}(./.claude)${reset} - this project only
`);

  return new Promise((resolve) => {
    rl.question(`  Choice ${dim}[1]${reset}: `, async (answer) => {
      rl.close();
      const choice = answer.trim() || '1';
      const isGlobal = choice !== '2';
      await install(isGlobal);
      resolve();
    });
  });
}

// Main
async function main() {
  if (hasGlobal && hasLocal) {
    console.error(`  ${yellow}Cannot specify both --global and --local${reset}`);
    process.exit(1);
  } else if (explicitConfigDir && hasLocal) {
    console.error(`  ${yellow}Cannot use --config-dir with --local${reset}`);
    process.exit(1);
  } else if (hasGlobal) {
    await install(true);
  } else if (hasLocal) {
    await install(false);
  } else {
    await promptLocation();
  }
}

main().catch((err) => {
  console.error(`  ${yellow}Error: ${err.message}${reset}`);
  process.exit(1);
});
