---
title: Code blocks
icon: material/code-json
---
# Code blocks
> Reference [:octicons-link-external-16: Code blocks - :simple-materialformkdocs: Material for MkDocs](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/)

## Python block with line highlighting and line numbers
```python hl_lines="2" linenums="1"
def hello():
    print("Hello, world!")
```

Using the `hl_lines` attribute, you can highlight specific
lines in the code block.
````md
```python hl_lines="2" linenums="1"
...
```
````

## JavaScript block
```javascript
function hello() {
    console.log("Hello, world!");
}
```
/// html | div.result
```text
Hello, world!
```
///

## Bash block
```bash
echo "Hello, world!"
```

## Collapsable block

/// collapse-code
```java title="LongClass.java"
class LongClass {
    private int a;
    public LongClass() {
        a = 0;
    }

    public void increment() {
        a++;
    }

    public void decrement() {
        a--;
    }

    public int getA() {
        return a;
    }

    public void setA(int a) {
        this.a = a;
    }
}
```
///

## Downloadable block

From file:
```java {title="HelloWorld.java" data-download="../../files/HelloWorld.java"}
--8<-- "docs/files/HelloWorld.java"
```

````md
```java {title="HelloWorld.java" data-download="../../files/HelloWorld.java"}
\--8<-- "docs/files/HelloWorld.java"
```
````

From content:
```java {title="HelloWorld.java" data-download="1"}
--8<-- "docs/files/HelloWorld.java"
```
````md
```java {title="HelloWorld.java" data-download="1"}
\--8<-- "docs/files/HelloWorld.java"
```
````

## Shell block
```shellconsole
joapuiib@FP:~/git_tutorial (main) $ echo "Hello world!"
(venv) joapuiib@FP:~/git_tutorial (main) $ git diff
diff --git a/README.md b/README.md
index 6d747b3..ff524e4 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,4 @@
 # Tutorial de Git
 Estem aprenent a utilitzar Git!
+
+Hem modificat un fitxer existent.
-Hem eliminat un fitxer.
joapuiib@FP:~/git_tutorial (main) $ git push
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
To /home/joapuiib/gitflow_example/remot
   0fb88ef..9e34bb0  develop -> develop
```

### Git log
```shellconsole
joapuiib@FP:~/git_tutorial (main) $ git lga
* f853946 - (7 minutes ago) README: Afegits autors - Mar (origin/feature/author)
| * cc8c388 - (9 minutes ago) LICENSE: Afegida llicència - Pau (origin/feature/license)
|/  
| * 9e34bb0 - (15 minutes ago) README: Afegida descripció del projecte - Anna (HEAD -> develop, origin/develop, feature/readme, origin/feature/readme)
|/  
* 0fb88ef - (29 minutes ago) 1. Primer commit - Joan Puigcerver (origin/main, origin/HEAD, main)
[user@host ~ (main)] $ echo "Hello, world!"
(venv) [user@host ~] $ echo "Hello, world!"
```

### Git status
```shellconsole
joapuiib@FP:~/git_tutorial (main) $ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        deleted:    README.md
	    modified:   mkdocs.yml
	    modified:   requirements.txt

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
```

### Git show
```shellconsole
joapuiib@FP:~/01_introduccio (main) $ git show 8e70293
commit 8e702933d5dbec9ee71100a1599ae4491085e1aa (HEAD -> main, tag: v1, origin/main, origin/HEAD)
Author: Joan Puigcerver Ibáñez <j.puigcerveribanez@edu.gva.es>
Date:   Fri Oct 13 16:06:59 2023 +0200

    Added README.md

diff --git a/README.md b/README.md
new file mode 100644
index 0000000..6d747b3
--- /dev/null
+++ b/README.md
@@ -0,0 +1,2 @@
+# 01 - Introducció a Git
+Estem aprenent a utilitzar Git!
```

### Git output with hints and errors
```shellconsole
joapuiib@FP:~/git_tutorial (main) $ git init
hint: Using 'master' as the name for the initial branch. This default branch name
hint: is subject to change. To configure the initial branch name to use in all
hint: of your new repositoris, which will suppress this warning, call:
hint:
hint: git config --global init.dafaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: git branch -m <name>
Initialized empty Git repository in /home/joapuiib/git_tutorial/.git/
fatal: unable to auto-detect email address (got 'joapuiib@FP.(none)')
```

## Keyboard keys
++ctrl+alt+del++

```md
++ctrl+alt+del++
```
