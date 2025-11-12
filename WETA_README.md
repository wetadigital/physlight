Welcome to the Wētā FX internal readme for physlight
====================================================

This repo is actively synced from [the upstream repository (external)](https://github.com/wetadigital/physlight.git).

Legalities
----------

While not all commits to this repo will be committed back to the opensource community, it is easier if we assume that they are.
This makes it easier to push commits at a later date if we do decide to contribute them etc.

Therefore, all commits *must* include a [Developer Certificate of Origin (DCO)](https://wiki.linuxfoundation.org/dco) 
sign off. This certifies that you agree to the terms at https://developercertificate.org/. In short, it states you wrote the code 
yourself without copying / transcribing it from somewhere.

This should be done using your Wētā FX username and email address:
For example:

`Signed-off-by: Jane Doe <jdoe@wetafx.co.nz>`

> **TIP:** You can apply a DCO signoff using the following git commit command:
> ```bash
> git commit -m "Test" --signoff
> ```

Wētā FX has a signed contributor agreement (CLA) in place.

As a company, we will also be adding the review chain to that contribution (much like the linux kernel does 
where at the end of a commit comment, you will see a chain of Signed-off-by), which should provide confidence for the 
upstream project to accept it more readily.

Brand new files that are added as part of adding a feature shall include a copyright notice as a comment as the first line. 
Additionally, an SPDX License Identifier (see https://spdx.org) or similar that is appropriate for that project should be 
added in accordance with the upstream project policies. Something like the following for C++

```c++
// Copyright © 2024, Wētā FX, Ltd.
// SPDX-License-Identifier: Apache-2.0
```

Contributing
------------

Make sure to read the OSS Contributing Guidelines if available in the upstream repository.

Namespacing
-----------

All git tags and branches created internally should be prefixed with `weta/`. This avoids collisions with upstream refs.

Workflow
--------

As we have changes that are internal only, we have a `weta/main` branch. This 
functions like the `main` branch would in any other repo, but will be updated with the upstream from time to time.

Due to the syncing nature of this, there are a few branches that we maintain:

* `weta/main` - the internal main branch, with all our internal only changes.
* `weta/RB-X.Y.Z` - this is the branch for a specific release of physlight, and is branched off the upstream release tag. It allows patches to be made for that release.
* `weta/user/$USERNAME/$BRANCHNAME` - This is your working branch. It should branch off `weta/main` or `weta/RB-X.Y.Z`

At the moment, only repo maintainers can merge into the first 2 branch types. We will look at opening that up as we get more familiar with this process and work out any issues.

To make a change, make a `weta/user/$USERNAME/$BRANCHNAME` branch off either `weta/main` (most common) or `weta/RB-X.Y.Z` (to patch a specific release).

Local Merges
------------

Once your changes have been made, you can merge these back into the weta internal branches like normal. That is, you can push up an MR, have it reviewed and merged!

Build and Release
-----------------

TBC once the build files have been added