#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

// Colors
const cyan = '\x1b[38;2;47;167;160m'; // #2FA7A0
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
  development system for Claude Code by TÂCHES.
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
const hasHelp = args.includes('--help') || args.includes('-h');

console.log(banner);

// Show help if requested
if (hasHelp) {
  console.log(`  ${yellow}Usage:${reset} npx mindsystem-cc [options]

  ${yellow}Options:${reset}
    ${cyan}-g, --global${reset}              Install globally (to Claude config directory)
    ${cyan}-l, --local${reset}               Install locally (to ./.claude in current directory)
    ${cyan}-c, --config-dir <path>${reset}   Specify custom Claude config directory
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
 * Install to the specified directory
 */
function install(isGlobal) {
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

  // Create commands directory
  const commandsDir = path.join(claudeDir, 'commands');
  fs.mkdirSync(commandsDir, { recursive: true });

  // Copy commands/ms with path replacement
  const msSrc = path.join(src, 'commands', 'ms');
  const msDest = path.join(commandsDir, 'ms');
  copyWithPathReplacement(msSrc, msDest, pathPrefix);
  console.log(`  ${green}✓${reset} Installed commands/ms`);

  // Copy mindsystem skill with path replacement
  const skillSrc = path.join(src, 'mindsystem');
  const skillDest = path.join(claudeDir, 'mindsystem');
  copyWithPathReplacement(skillSrc, skillDest, pathPrefix);
  console.log(`  ${green}✓${reset} Installed mindsystem`);

  // Copy agents to ~/.claude/agents (subagents must be at root level)
  const agentsSrc = path.join(src, 'agents');
  if (fs.existsSync(agentsSrc)) {
    const agentsDest = path.join(claudeDir, 'agents');
    copyWithPathReplacement(agentsSrc, agentsDest, pathPrefix);
    console.log(`  ${green}✓${reset} Installed agents`);
  }

  // Copy scripts to ~/.claude/mindsystem/scripts/
  const scriptsSrc = path.join(src, 'scripts');
  if (fs.existsSync(scriptsSrc)) {
    const scriptsDest = path.join(claudeDir, 'mindsystem', 'scripts');
    fs.mkdirSync(scriptsDest, { recursive: true });
    const scriptEntries = fs.readdirSync(scriptsSrc, { withFileTypes: true });
    for (const entry of scriptEntries) {
      const srcPath = path.join(scriptsSrc, entry.name);
      const destPath = path.join(scriptsDest, entry.name);
      if (entry.isDirectory()) {
        // Recursively copy directories (like ms-lookup/)
        copyDir(srcPath, destPath);
      } else {
        fs.copyFileSync(srcPath, destPath);
        // Make shell scripts executable
        if (entry.name.endsWith('.sh')) {
          fs.chmodSync(destPath, '755');
        }
      }
    }
    console.log(`  ${green}✓${reset} Installed scripts`);

    // Check Python availability for ms-lookup
    const msLookupPath = path.join(scriptsDest, 'ms-lookup');
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
  }

  // Copy CHANGELOG.md
  const changelogSrc = path.join(src, 'CHANGELOG.md');
  const changelogDest = path.join(claudeDir, 'mindsystem', 'CHANGELOG.md');
  if (fs.existsSync(changelogSrc)) {
    fs.copyFileSync(changelogSrc, changelogDest);
    console.log(`  ${green}✓${reset} Installed CHANGELOG.md`);
  }

  // Write VERSION file for whats-new command
  const versionDest = path.join(claudeDir, 'mindsystem', 'VERSION');
  fs.writeFileSync(versionDest, pkg.version);
  console.log(`  ${green}✓${reset} Wrote VERSION (${pkg.version})`);

  console.log(`
  ${green}Done!${reset} Launch Claude Code and run ${cyan}/ms:help${reset}.
`);
}

/**
 * Prompt for install location
 */
function promptLocation() {
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

  rl.question(`  Choice ${dim}[1]${reset}: `, (answer) => {
    rl.close();
    const choice = answer.trim() || '1';
    const isGlobal = choice !== '2';
    install(isGlobal);
  });
}

// Main
if (hasGlobal && hasLocal) {
  console.error(`  ${yellow}Cannot specify both --global and --local${reset}`);
  process.exit(1);
} else if (explicitConfigDir && hasLocal) {
  console.error(`  ${yellow}Cannot use --config-dir with --local${reset}`);
  process.exit(1);
} else if (hasGlobal) {
  install(true);
} else if (hasLocal) {
  install(false);
} else {
  promptLocation();
}
