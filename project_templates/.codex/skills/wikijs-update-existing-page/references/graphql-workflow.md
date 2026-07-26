# Wiki.js GraphQL workflow reference

## Endpoints

- Page API: `${WIKIJS_URL}/graphql`
- Asset upload API: `${WIKIJS_URL}/u`

## Known page schema shape for Wiki.js v2.x

Common query patterns:

### List pages

```graphql
query ListPages($locale: String) {
  pages {
    list(locale: $locale) {
      id
      path
      locale
      title
      description
      contentType
      updatedAt
    }
  }
}
```

### Get one page by path

```graphql
query SingleByPath($path: String!, $locale: String!) {
  pages {
    singleByPath(path: $path, locale: $locale) {
      id
      path
      locale
      title
      description
      content
      render
      contentType
      updatedAt
    }
  }
}
```

### Create page

```graphql
mutation CreatePage(
  $content: String!
  $description: String!
  $editor: String!
  $isPublished: Boolean!
  $isPrivate: Boolean!
  $locale: String!
  $path: String!
  $tags: [String]!
  $title: String!
  $scriptCss: String
  $scriptJs: String
) {
  pages {
    create(
      content: $content
      description: $description
      editor: $editor
      isPublished: $isPublished
      isPrivate: $isPrivate
      locale: $locale
      path: $path
      tags: $tags
      title: $title
      scriptCss: $scriptCss
      scriptJs: $scriptJs
    ) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
      page {
        id
        path
        title
      }
    }
  }
}
```

### Update page

```graphql
mutation UpdatePage(
  $id: Int!
  $content: String
  $description: String
  $editor: String
  $isPrivate: Boolean
  $isPublished: Boolean
  $locale: String
  $path: String
  $tags: [String]
  $title: String
  $scriptCss: String
  $scriptJs: String
) {
  pages {
    update(
      id: $id
      content: $content
      description: $description
      editor: $editor
      isPrivate: $isPrivate
      isPublished: $isPublished
      locale: $locale
      path: $path
      tags: $tags
      title: $title
      scriptCss: $scriptCss
      scriptJs: $scriptJs
    ) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
      page {
        id
        path
        title
      }
    }
  }
}
```

On the verified installation, create/update responses should request `page { id path title }` only. Requesting `page.locale` from the mutation response produced `Cannot return null for non-nullable field Page.locale` even when the page operation itself was valid.

## Asset folder schema

### List folders

```graphql
query AssetFolders($parentFolderId: Int!) {
  assets {
    folders(parentFolderId: $parentFolderId) {
      id
      slug
      name
    }
  }
}
```

### Create folder

```graphql
mutation CreateAssetFolder($parentFolderId: Int!, $slug: String!, $name: String) {
  assets {
    createFolder(parentFolderId: $parentFolderId, slug: $slug, name: $name) {
      responseResult {
        succeeded
        slug
        message
      }
    }
  }
}
```

Wiki.js `ghcr.io/requarks/wiki:2.5.308` exposes `createFolder` as `DefaultResponse`; the success fields are nested under `responseResult`. Do not use the direct `createFolder { succeeded ... }` shape because that fails GraphQL validation on this installation.

## Permissions

To create or update pages, the token or authenticated principal must satisfy the page mutation authorization requirements.
To upload assets, the principal must have asset write permission.

## Safe workflow

1. Resolve canonical page path first.
2. Check whether the page already exists.
3. If absent, create it.
4. If present, update it.
5. Upload screenshots one at a time.
6. Build asset references using the inferred final wiki asset path from the selected folder path and deterministic file name. The `/u` endpoint returns the literal body `ok`, not an asset JSON document.
7. Re-read the page after mutation when auditability matters.

