# Further work for this document

A readable worklist of various edits to apply to the document

## Align naming to a current standard

Resync all the names of photo/radio-metric quantities:
especially the use of exitance vs radiosity vs emittance is too casual, it should be tightened up

https://cie.co.at/publications/ilv-international-lighting-vocabulary-2nd-edition-0

IEC 60050-845: Lighting - https://webstore.iec.ch/publication/26592

https://www.iso.org/obp/ui/\#iso:std:iso:80000:-7:ed-2:v1:en

Consider in Table 1.1 making it more clear that certain quantities are spectral,
some readers have reported finding the division by 'm' to mean wavelength to be confusing,
as it's more often than not used in nanometers.
Repeating 'spectral' in all rows could be a way to go, except that it uses a lot of space.
It can be confusing that the radiometric column is spectral and the photometric one is not.

There is also a need to reconcile how a few new concepts introduced in the document
are called throughout. An example is the emission constant is sometimes called the
light constant.



## Generalize references to specific pipelines and workflows

The document originated as an internal work item from Weta Digital.
As such it contains several references to objects and concepts that are Weta-specific.
These should be rephrased to be more general instead.


## Make sure there is alignment between UsdLux and PhysLight

Two-way work item to make sure UsdLux and PhysLight are compatible.


## Improve calculation sheets chapter

Rebuild the calculation sheets chapter using pythontex or maybe cogapp instead of having hardcoded source

Make figures illustrating the scenarios in the various examples

## Other suggestions

Add a section describing the world of photography, covering what the main words and concepts are and how they are normally used,
to serve as background for reader unfamiliar with this field.

The section on sensor reference data and examples is excessively dry. Also as it stands
the LaTeX engine formats it poorly, and the pdf resulting is not as clear as it could be.


\todo{Make a pass to check that end-of-segment phrases all have or all don't have a full stop}



