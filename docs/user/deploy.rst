Deploying Your Simulation to GitHub Pages
==========================================

Once you have created a Brian2WASM simulation, you can deploy it online using
`GitHub Pages <https://pages.github.com/>`_. This allows others to view and run
your simulation directly in their browser without needing to install anything.

Prerequisites
-------------

1. Repository should contain ``your_script.py``, brian2wasm's ``pyproject.toml``.
2. Folder Structure can look something like

.. code-block:: text

   📁 root folder
    ├─ 📁 .github
    │   └─ 📁 workflows
    │       └─ 📄 deploy.yml
    ├─ 📁 brian2wasm
    ├─ 📁 examples
    ├─ 📄 your_script.py
    └─ 📄 pyproject.toml


Setup Instructions
------------------

1. **Create the GitHub Actions Workflow**

Create a file named ``.github/workflows/deploy.yml`` in your repository with the following content:

.. code-block:: yaml

      name: Deploy Brian2WASM Simulation to GitHub Pages

      on:
        push:
          branches: [ main ]
          paths:
            - ".github/workflows/deploy.yml"

      permissions:
        contents: write

      jobs:
        build-and-deploy:
          runs-on: ubuntu-latest

          env:
            SCRIPT: path/to/your/script.py  # 👈 Change this to your script path

          steps:
            - name: Checkout code
              uses: actions/checkout@v4

            - name: Install pixi
              uses: prefix-dev/setup-pixi@v0.8.0
              with:
                cache: false

            - name: Install dependencies
              run: pixi install --locked

            - name: Run setup
              run: pixi run setup

            - name: Derive folder paths
              id: derive
              run: |
                # remove .py extension
                FOLDER_PATH="${SCRIPT%.py}"
                # just the last folder name (e.g. ornstein_uhlenbeck)
                FOLDER_NAME=$(basename "$FOLDER_PATH")
                echo "FOLDER_PATH=$FOLDER_PATH" >> $GITHUB_ENV
                echo "FOLDER_NAME=$FOLDER_NAME" >> $GITHUB_ENV

            - name: Generate simulation files
              run: |
                python -m brian2wasm $SCRIPT --no-server
              shell: pixi run bash -e {0}

            - name: Deploy to gh-pages
              run: |
                git fetch origin gh-pages || true
                git checkout gh-pages || git checkout --orphan gh-pages

                rm -rf $FOLDER_NAME
                mkdir -p $FOLDER_NAME

                cp $FOLDER_PATH/brian.js \
                   $FOLDER_PATH/index.html \
                   $FOLDER_PATH/wasm_module.js \
                   $FOLDER_PATH/wasm_module.wasm \
                   $FOLDER_PATH/worker.js \
                   $FOLDER_NAME/ || true

                cat > index.html <<EOF
                <!doctype html>
                <html lang="en">
                <head>
                  <meta charset="utf-8">
                  <title>${GITHUB_ACTOR}'s brian2wasm simulations</title>
                  <style>
                    body {
                      font-family: Arial, sans-serif;
                      margin: 40px auto;
                      max-width: 700px;
                      text-align: center;
                      background: #fafafa;
                    }
                    h1 {
                      font-size: 2em;
                      margin-bottom: 1em;
                      color: #222;
                    }
                    ul {
                      list-style: disc;
                      text-align: left;
                      display: inline-block;
                      font-size: 1.2em;
                      line-height: 1.6;
                    }
                    a {
                      text-decoration: none;
                      color: #007acc;
                    }
                    a:hover {
                      text-decoration: underline;
                    }
                  </style>
                </head>
                <body>
                  <h1>${GITHUB_ACTOR}'s brian2wasm simulations</h1>
                  <ul>
                EOF

                for d in */ ; do
                  if [ -f "$d/index.html" ]; then
                    NAME=$(basename "$d")
                    echo "    <li><a href=\"$NAME/\">$NAME</a></li>" >> index.html
                  fi
                done

                cat >> index.html <<EOF
                  </ul>
                </body>
                </html>
                EOF

                git add $FOLDER_NAME index.html
                git -c user.name='github-actions' -c user.email='github-actions@github.com' \
                  commit -m "Deploy $FOLDER_NAME" || echo "No changes"
                git push -f https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }} gh-pages

2. **Configure Your Script Path**

   In the workflow file, change the ``SCRIPT`` environment variable to point to your Brian2WASM simulation script:

   .. code-block:: yaml

      env:
        SCRIPT: examples/ornstein_uhlenbeck.py  # Replace with your script path

3. **Commit and Push the Workflow**

   Add the workflow file to your repository and push it to the ``main`` branch:

   .. code-block:: bash

      git add .github/workflows/deploy.yml
      git commit -m "Add GitHub Pages deployment workflow"
      git push origin main

4. **Enable GitHub Pages (First Time Only)**

   This step only needs to be done once for your repository:

   a. Go to your repository on GitHub
   b. Click on **Settings** tab
   c. Scroll down to **Pages** in the left sidebar
   d. Under **Source**, select **Deploy from a branch**
   e. Choose **gh-pages** as the branch
   f. Select **/ (root)** as the folder
   g. Click **Save**

   .. image:: ../images/setup_github_pages.png


5. **Wait For GitHub Actions To Complete**

   After committing your changes, go to the **Actions** tab in your repository.
   You will notice that **two workflows** run automatically:

   1. **Deploy Brian2WASM Simulation to GitHub Pages** → builds your Brian2WASM output and pushes it to the ``gh-pages`` branch.
   2. **pages-build-deployment** → takes the content from the ``gh-pages`` branch and publishes it live on your GitHub Pages site.

   .. image:: ../images/actions_two_steps.png


6. **Access Your Deployed Simulation**

   You can access your deployment in two ways:

   1. Go to **Actions > Deployment > View deployment** and click the provided link.
   2. Directly visit:
      ``https://<your-username>.github.io/<your-repository-name>/``

   Individual simulations will be available at:
   ``https://<your-username>.github.io/<your-repository-name>/<simulation-name>/``

   .. image:: ../images/access_deployment.png

   .. note::

      Deployed simulations look like this:
      https://palashchitnavis.github.io/brian2wasm/
